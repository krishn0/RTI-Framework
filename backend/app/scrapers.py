"""Compliant collector modules.

The generic collectors intentionally stay conservative: they only follow same-origin,
public links advertised by a registered source. Source-specific selectors can extend
these classes without changing versioning, logging, or safety behaviour.
"""
from __future__ import annotations

import json
import ipaddress
import re
import socket
import time
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from . import models
from .ingestion import USER_AGENT, detect_district, extract_mentions, ingest_document, ingest_youtube, parse_article_html, sha256, video_id_from_url


@dataclass
class CollectedItem:
    url: str
    title: str
    kind: str = "page"
    metadata: dict | None = None


class BaseScraper(ABC):
    """Fetch → parse → normalize → download → save → run contract."""

    def __init__(self, db: Session, source: models.Source, run: models.ScraperRun):
        self.db, self.source, self.run_record = db, source, run
        self.client = httpx.Client(timeout=25, follow_redirects=True, headers={"User-Agent": USER_AGENT})
        self._last_request_at = 0.0
        self._robots: dict[str, RobotFileParser] = {}
        self._verified_public_hosts: set[str] = set()

    def log(self, level: str, message: str, context: dict | None = None):
        self.db.add(models.ScraperLog(run_id=self.run_record.id, source_id=self.source.id, level=level, message=message, context=json.dumps(context) if context else None))
        self.db.flush()

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            robots = RobotFileParser(urljoin(origin, "/robots.txt"))
            try:
                response = self.client.get(robots.url)
                if response.status_code < 400:
                    robots.parse(response.text.splitlines())
                else:
                    robots.parse([])
            except httpx.HTTPError:
                # Unavailable robots files are logged; collectors remain restricted
                # to the explicitly registered origin.
                robots.parse([])
                self.log("WARNING", "robots.txt could not be fetched", {"origin": origin})
            self._robots[origin] = robots
        return self._robots[origin].can_fetch(USER_AGENT, url)

    def _rate_limit(self):
        wait = max(0, self.source.crawl_delay - (time.monotonic() - self._last_request_at))
        if wait:
            time.sleep(wait)

    def fetch(self, url: str | None = None, allow_cross_origin: bool = False) -> httpx.Response:
        target = url or self.source.base_url
        if urlparse(target).scheme not in {"http", "https"}:
            raise PermissionError("Only public HTTP(S) collection is allowed")
        if urlparse(target).netloc != urlparse(self.source.base_url).netloc and not allow_cross_origin:
            raise PermissionError("Cross-origin collection is not allowed")
        host = urlparse(target).hostname
        if allow_cross_origin and host not in self._verified_public_hosts:
            try:
                addresses = {entry[4][0] for entry in socket.getaddrinfo(host, None)}
            except socket.gaierror as exc:
                raise PermissionError("Linked asset host could not be resolved") from exc
            if any((ipaddress.ip_address(address).is_private or ipaddress.ip_address(address).is_loopback or ipaddress.ip_address(address).is_link_local) for address in addresses):
                raise PermissionError("Linked private-network assets are not allowed")
            self._verified_public_hosts.add(host)
        if not self.allowed(target):
            raise PermissionError(f"robots.txt disallows collection: {target}")
        self._rate_limit()
        response = None
        for attempt, backoff in enumerate((0, 2, 4, 8)):
            if backoff:
                time.sleep(backoff)
            try:
                if self.source.requires_javascript and target.rstrip("/") == self.source.base_url.rstrip("/"):
                    with sync_playwright() as playwright:
                        browser = playwright.chromium.launch(headless=True)
                        page = browser.new_page(user_agent=USER_AGENT)
                        page.goto(target, wait_until="networkidle", timeout=30000)
                        response = httpx.Response(200, text=page.content(), request=httpx.Request("GET", target))
                        browser.close()
                else:
                    response = self.client.get(target)
                if response.status_code < 500:
                    break
            except httpx.TransportError:
                if attempt == 3:
                    raise
        if response is None:
            raise httpx.TransportError("Source did not return a response")
        self._last_request_at = time.monotonic()
        response.raise_for_status()
        return response

    def parse(self, response: httpx.Response) -> list[CollectedItem]:
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        for link in soup.select("a[href]"):
            url = urljoin(str(response.url), link.get("href"))
            if urlparse(url).netloc == urlparse(self.source.base_url).netloc:
                items.append(CollectedItem(url=url, title=link.get_text(" ", strip=True) or url))
        return items

    def normalize(self, items: list[CollectedItem]) -> list[CollectedItem]:
        unique = {}
        for item in items:
            item.url = item.url.split("#", 1)[0]
            if item.url not in unique:
                unique[item.url] = item
        return list(unique.values())[:50]

    def download(self, item: CollectedItem) -> bytes:
        return self.fetch(item.url, allow_cross_origin=True).content

    def save(self, item: CollectedItem, content: bytes | None = None) -> str:
        return "observed"

    def run(self) -> dict[str, int]:
        response = self.fetch()
        items = self.normalize(self.parse(response))
        result = {"found": len(items), "created": 0, "updated": 0, "duplicates": 0, "pages_scanned": 1, "errors": 0}
        for item in items:
            try:
                outcome = self.save(item)
                if outcome == "created": result["created"] += 1
                elif outcome == "versioned": result["updated"] += 1
                elif outcome == "duplicate": result["duplicates"] += 1
                self.db.commit()
            except (httpx.HTTPError, PermissionError, ValueError) as exc:
                result["errors"] += 1
                self.log("WARNING", f"Item skipped: {exc}", {"url": item.url})
        self.log("INFO", "Collection completed", result)
        self.client.close()
        return result


class GovernmentWebsiteScraper(BaseScraper):
    """Discovers public documents linked by a government landing page."""

    def parse(self, response: httpx.Response) -> list[CollectedItem]:
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        for link in soup.select("a[href]"):
            url = urljoin(str(response.url), link.get("href"))
            if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).path.lower().endswith(".pdf"):
                continue
            container = link.find_parent("tr")
            title = container.get_text(" ", strip=True) if container else link.get_text(" ", strip=True)
            title = re.sub(r"\b(view|download)\b", "", title, flags=re.I).strip(" -|") or self.source.name
            date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", title)
            published_at = None
            if date_match:
                try:
                    published_at = datetime(int(date_match.group(3)), int(date_match.group(2)), int(date_match.group(1)), tzinfo=timezone.utc)
                except ValueError:
                    pass
            items.append(CollectedItem(url, title[:600], "document", {"published_at": published_at}))
        return items

    def save(self, item: CollectedItem, content: bytes | None = None) -> str:
        data = content or self.download(item)
        if not data.startswith(b"%PDF"):
            raise ValueError("Advertised PDF did not contain PDF content")
        _, outcome = ingest_document(self.db, source=self.source, title=item.title, url=item.url, data=data, department=self.source.name, published_at=(item.metadata or {}).get("published_at"))
        self.db.flush()
        return outcome

    def run(self) -> dict[str, int]:
        if self.source.input_kind == "pdf" or urlparse(self.source.base_url).path.lower().endswith(".pdf"):
            result = {"found": 1, "created": 0, "updated": 0, "duplicates": 0, "pages_scanned": 1, "errors": 0}
            try:
                outcome = self.save(CollectedItem(self.source.base_url, self.source.name, "document"))
                key = "updated" if outcome == "versioned" else "duplicates" if outcome == "duplicate" else "created"
                result[key] += 1
                self.db.commit()
                self.log("INFO", "Direct PDF collection completed", result)
            except Exception as exc:
                result["errors"] = 1; self.log("ERROR", str(exc), {"url": self.source.base_url})
            self.client.close()
            return result
        result = {"found": 0, "created": 0, "updated": 0, "duplicates": 0, "pages_scanned": 0, "errors": 0}
        try:
            landing = self.fetch()
            result["pages_scanned"] = 1
            all_links = self.normalize(BaseScraper.parse(self, landing))
            pdfs = [CollectedItem(x.url, x.title, "document") for x in all_links if urlparse(x.url).path.lower().endswith(".pdf")]
            keywords = ("document", "download", "notice", "circular", "publication", "resolution", "budget", "report", "tender", "/gr")
            candidate_pages = [x for x in all_links if not urlparse(x.url).path.lower().endswith(".pdf") and any(k in (x.url + " " + x.title).lower() for k in keywords)][:8]
            for page_link in candidate_pages:
                try:
                    page = self.fetch(page_link.url)
                    result["pages_scanned"] += 1
                    pdfs.extend(self.parse(page))
                except (httpx.HTTPError, PermissionError) as exc:
                    self.log("WARNING", f"Discovery page skipped: {exc}", {"url": page_link.url})
            pdfs = self.normalize(pdfs)
            result["found"] = len(pdfs)
            for item in pdfs:
                try:
                    outcome = self.save(item)
                    key = "updated" if outcome == "versioned" else "duplicates" if outcome == "duplicate" else "created"
                    result[key] += 1
                    self.db.commit()
                except Exception as exc:
                    result["errors"] += 1
                    self.log("WARNING", f"Document skipped: {exc}", {"url": item.url})
            self.log("INFO", "Government document discovery completed", result)
        except Exception as exc:
            result["errors"] += 1
            self.log("ERROR", str(exc), {"url": self.source.base_url})
        self.client.close()
        return result


class GovernmentDocumentScraper(GovernmentWebsiteScraper):
    department: str | None = None
    category: str | None = None

    def save(self, item: CollectedItem, content: bytes | None = None) -> str:
        data = content or self.download(item)
        if not data.startswith(b"%PDF"):
            raise ValueError("Advertised PDF did not contain PDF content")
        _, outcome = ingest_document(self.db, source=self.source, title=item.title, url=item.url, data=data, department=self.department or self.source.name, category=self.category, published_at=(item.metadata or {}).get("published_at"))
        self.db.flush()
        return outcome


class FinanceScraper(GovernmentDocumentScraper):
    department = "Finance Department"
    category = "Finance & Budget"


class PWDScraper(GovernmentDocumentScraper):
    department = "Public Works Department"
    category = "Public Works"


class TenderScraper(GovernmentDocumentScraper):
    category = "Tender"


class GazetteScraper(GovernmentDocumentScraper):
    category = "Gazette"


class NewsScraper(BaseScraper):
    def run(self) -> dict[str, int]:
        if self.source.input_kind == "news article":
            result = {"found": 1, "created": 0, "updated": 0, "duplicates": 0, "pages_scanned": 1, "errors": 0}
            try:
                outcome = self.save(CollectedItem(self.source.base_url, self.source.name, "article"))
                result["duplicates" if outcome == "duplicate" else "created"] += 1
                self.db.commit()
                self.log("INFO", "Direct news article collection completed", result)
            except Exception as exc:
                result["errors"] = 1; self.log("ERROR", str(exc), {"url": self.source.base_url})
            self.client.close()
            return result
        return super().run()

    def parse(self, response: httpx.Response) -> list[CollectedItem]:
        soup = BeautifulSoup(response.text, "html.parser")
        candidates = soup.select("article a[href], main h2 a[href], main h3 a[href]")
        return [CollectedItem(urljoin(str(response.url), a.get("href")), a.get_text(" ", strip=True), "article") for a in candidates]

    def save(self, item: CollectedItem, content: bytes | None = None) -> str:
        response = self.fetch(item.url)
        parsed = parse_article_html(item.url, response.text)
        if len(parsed["article_text"]) < 120:
            raise ValueError("Page did not contain enough article text")
        digest = sha256(parsed["article_text"].encode("utf-8"))
        existing = self.db.query(models.NewsArticle).filter(
            (models.NewsArticle.canonical_url == parsed["canonical_url"]) | (models.NewsArticle.sha256 == digest)
        ).first()
        if existing:
            existing.last_seen_at = datetime.now(timezone.utc)
            return "duplicate"
        location = detect_district(f'{parsed["title"]} {parsed["article_text"][:5000]}')
        row = models.NewsArticle(source_id=self.source.id, publisher=self.source.name, title=parsed["title"], article_url=item.url, canonical_url=parsed["canonical_url"], author=parsed["author"], published_at=parsed["published_at"], description=parsed["description"], article_text=parsed["article_text"], language=parsed["language"], image_url=parsed["image_url"], location=location, sha256=digest, mentions=extract_mentions(parsed["article_text"]))
        self.db.add(row)
        self.db.flush()
        from .ingestion import index_content
        index_content(self.db, "news_article", row.id, row.title, row.publisher, row.article_url, row.article_text, source_id=self.source.id, district=row.location, publisher=row.publisher)
        return "created"


class YouTubeTranscriptScraper(BaseScraper):
    """Channel/playlist discovery adapter; individual video ingestion uses /api/youtube/scrape."""

    def run(self) -> dict[str, int]:
        result = {"found": 0, "created": 0, "updated": 0, "duplicates": 0, "pages_scanned": 1, "errors": 0}
        try:
            video_id = video_id_from_url(self.source.base_url)
            video_urls = [self.source.base_url] if video_id else self.discover_channel_videos()
            result["found"] = len(video_urls)
            for position, url in enumerate(video_urls):
                if position:
                    time.sleep(self.source.crawl_delay)
                current_id = video_id_from_url(url)
                existed = self.db.query(models.YouTubeVideo).filter_by(video_id=current_id).first() is not None
                try:
                    ingest_youtube(self.db, url, source=self.source)
                    result["duplicates" if existed else "created"] += 1
                except Exception as exc:
                    result["errors"] += 1
                    self.log("WARNING", f"Video transcript skipped: {exc}", {"url": url})
            self.log("INFO", "YouTube transcript collection completed", result)
        except Exception as exc:
            result["errors"] = 1; self.log("ERROR", str(exc), {"url": self.source.base_url})
        self.client.close()
        return result

    def discover_channel_videos(self) -> list[str]:
        target = self.source.base_url.rstrip("/")
        if not target.endswith("/videos"):
            target += "/videos"
        page = self.fetch(target)
        # The public channel page contains its current video grid in ytInitialData.
        # This avoids YouTube's /feeds/videos.xml path, which robots.txt disallows.
        video_ids = list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', page.text)))
        if not video_ids:
            raise ValueError("No public videos were discoverable on the channel page")
        return [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids[:5]]


SCRAPER_REGISTRY = {
    "government_website": GovernmentWebsiteScraper,
    "government_document": PWDScraper,
    "tender_portal": TenderScraper,
    "gazette": GazetteScraper,
    "audit": GovernmentDocumentScraper,
    "court": GovernmentDocumentScraper,
    "news": NewsScraper,
    "youtube": YouTubeTranscriptScraper,
}


def scraper_for(source: models.Source):
    if "finance" in source.name.lower():
        return FinanceScraper
    return SCRAPER_REGISTRY.get(source.source_type, BaseScraper)
