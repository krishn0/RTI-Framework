"""Single-instance live collection scheduler.

For horizontally scaled deployments, run this scheduler in exactly one worker or
replace it with a distributed queue while retaining the same execute_run contract.
"""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from . import models
from .database import SessionLocal


_scheduler = BackgroundScheduler(timezone="UTC", daemon=True)
_workers = ThreadPoolExecutor(max_workers=4, thread_name_prefix="collector")


def frequency_seconds(value: str) -> int:
    normalized = (value or "daily").lower().strip()
    fixed = {"hourly": 3600, "daily": 86400, "weekly": 604800}
    if normalized in fixed:
        return fixed[normalized]
    match = re.fullmatch(r"every\s+(\d+)\s*(minute|minutes|hour|hours|day|days)", normalized)
    if not match:
        return 86400
    amount, unit = int(match.group(1)), match.group(2)
    multiplier = 60 if unit.startswith("minute") else 3600 if unit.startswith("hour") else 86400
    return max(60, amount * multiplier)


def next_run_for(frequency: str, after: datetime | None = None) -> datetime:
    return (after or datetime.now(timezone.utc)) + timedelta(seconds=frequency_seconds(frequency))


def poll_due_sources():
    now = datetime.now(timezone.utc)
    due_ids = []
    with SessionLocal() as db:
        for source in db.query(models.Source).filter_by(enabled=True).all():
            next_run = source.next_run_at
            # SQLite may return naive values even for timezone-aware columns.
            if next_run and next_run.tzinfo is None:
                next_run = next_run.replace(tzinfo=timezone.utc)
            active = db.query(models.ScraperRun).filter(models.ScraperRun.source_id == source.id, models.ScraperRun.status.in_(("queued", "running"))).first()
            if not active and (next_run is None or next_run <= now):
                run = models.ScraperRun(source_id=source.id, status="queued")
                db.add(run); db.flush(); due_ids.append(run.id)
                # Claim it before releasing this transaction.
                source.next_run_at = next_run_for(source.frequency, now)
        db.commit()
    if due_ids:
        from .main import execute_run
        for run_id in due_ids:
            _workers.submit(execute_run, run_id)


def start_scheduler():
    if not _scheduler.running:
        _scheduler.add_job(poll_due_sources, "interval", seconds=30, id="source-poller", replace_existing=True, max_instances=1, coalesce=True, next_run_time=datetime.now(timezone.utc))
        _scheduler.start()


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
