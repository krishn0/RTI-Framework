"""Structured query parsing and deterministic relevance scoring."""
import re
from dataclasses import dataclass, field


FILLER_WORDS = {
    "show", "find", "give", "tell", "me", "in", "the", "about", "information",
    "please", "all", "any", "for", "of", "on", "with", "from", "related",
    "to", "is", "are", "a", "an", "what", "which", "how", "list", "get", "details",
    "काय", "माहिती", "द्या", "दाखवा", "बघा",
}

LOCATIONS = {
    "Pune": (
        "pune", "poona", "पुणे", "पुण्यात", "पुण्यातील", "पुण्याच्या",
        "पुण्यातल्या", "पुण्यातून", "पुण्याला", "पुण्यासाठी", "पुणेकर",
    ),
    "Mumbai": (
        "mumbai", "bombay", "मुंबई", "मुंबईत", "मुंबईतील", "मुंबईच्या",
        "मुंबईतल्या", "मुंबईतून", "मुंबईला", "मुंबईसाठी",
    ),
    "Nagpur": ("nagpur", "नागपूर", "नागपुरात", "नागपुरातील", "नागपूरच्या", "नागपूरला"),
    "Nashik": ("nashik", "nasik", "नाशिक", "नाशिकमध्ये", "नाशिकातील", "नाशिकच्या", "नाशिकला"),
    "Thane": ("thane", "ठाणे", "ठाण्यात", "ठाण्यातील", "ठाण्याच्या", "ठाण्याला"),
    "Kolhapur": ("kolhapur", "कोल्हापूर", "कोल्हापुरात", "कोल्हापुरातील", "कोल्हापूरच्या"),
    "Ratnagiri": ("ratnagiri", "रत्नागिरी", "रत्नागिरीत", "रत्नागिरीतील"),
    "Sindhudurg": ("sindhudurg", "सिंधुदुर्ग", "सिंधुदुर्गात", "सिंधुदुर्गातील"),
    "Raigad": ("raigad", "रायगड", "रायगडात", "रायगडातील"),
    "Satara": ("satara", "सातारा", "साताऱ्यात", "साताऱ्यातील", "साताऱ्याच्या"),
    "Sangli": ("sangli", "सांगली", "सांगलीत", "सांगलीतील", "सांगलीच्या"),
    "Solapur": ("solapur", "सोलापूर", "सोलापुरात", "सोलापुरातील", "सोलापूरच्या"),
    "Aurangabad": (
        "aurangabad", "chhatrapati sambhajinagar", "sambhajinagar",
        "छत्रपती संभाजीनगर", "संभाजीनगर", "औरंगाबाद", "संभाजीनगरात", "औरंगाबादेत",
    ),
    "Ahmednagar": ("ahmednagar", "ahilyanagar", "अहमदनगर", "अहिल्यानगर"),
    "Akola": ("akola", "अकोला", "अकोल्यात"),
    "Amravati": ("amravati", "अमरावती", "अमरावतीत"),
    "Beed": ("beed", "बीड", "बीडला", "बीडमध्ये"),
    "Bhandara": ("bhandara", "भंडारा", "भंडाऱ्यात"),
    "Buldhana": ("buldhana", "बुलढाणा", "बुलढाण्यात"),
    "Chandrapur": ("chandrapur", "चंद्रपूर", "चंद्रपुरात"),
    "Dhule": ("dhule", "धुळे", "धुळ्यात"),
    "Gadchiroli": ("gadchiroli", "गडचिरोली"),
    "Gondia": ("gondia", "गोंदिया"),
    "Hingoli": ("hingoli", "हिंगोली"),
    "Jalgaon": ("jalgaon", "जळगाव", "जळगावात"),
    "Jalna": ("jalna", "जालना", "जालन्यात"),
    "Latur": ("latur", "लातूर", "लातुरात"),
    "Nanded": ("nanded", "नांदेड", "नांदेडात"),
    "Nandurbar": ("nandurbar", "नंदुरबार"),
    "Osmanabad": ("osmanabad", "dharashiv", "उस्मानाबाद", "धाराशिव"),
    "Palghar": ("palghar", "पालघर"),
    "Parbhani": ("parbhani", "परभणी"),
    "Wardha": ("wardha", "वर्धा"),
    "Washim": ("washim", "वाशीम"),
    "Yavatmal": ("yavatmal", "यवतमाळ"),
}

PROJECT_TYPES = {
    "road": (
        "road", "roads", "road project", "roadwork", "highway", "highways",
        "bridge", "bridges", "flyover", "flyovers", "expressway", "street", "streets",
        "रस्ता", "रस्ते", "रस्त्यांचा", "रस्त्यांची", "रस्त्यांचे", "रस्त्याचा",
        "रस्त्याची", "रस्त्यासाठी", "रस्त्यांवर", "रस्त्यावर", "रस्त्यांच्या",
        "मार्ग", "महामार्ग", "पूल", "सड़क", "सड़कें", "सड़कों", "सड़क", "सड़कें", "सड़कों",
        "फ्लाईओव्हर", "उड्डाणपूल", "पाणंद रस्ता", "पाणंद",
    ),
    "metro": (
        "metro", "metro project", "metro rail", "metro train", "मेट्रो",
        "मेट्रो प्रकल्प", "मेट्रो विस्तार", "मेट्रो मार्ग", "मेट्रो रेल्वे",
    ),
    "water": (
        "water", "water supply", "irrigation", "dam", "dams", "jal",
        "जल", "पाणी", "पाणीपुरवठा", "सिंचन", "धरण", "धरणे", "जलसंपदा",
    ),
    "housing": (
        "housing", "housing project", "pradhan mantri awas", "mhada",
        "घरकुल", "गृहनिर्माण", "म्हाडा", "घरकुले", "आवास",
    ),
    "railway": (
        "railway", "railways", "rail project", "train", "station",
        "रेल्वे", "रेल्वे प्रकल्प", "रेल्वे मार्ग", "रेल्वे सेवा",
    ),
    "infrastructure": (
        "infrastructure", "development", "पायाभूत सुविधा", "नागरी विकास",
        "विकास कामे", "विकास", "बुनियादी ढांचा",
    ),
}

DEPARTMENTS = {
    "Public Works Department": (
        "pwd", "public works", "public works department",
        "सार्वजनिक बांधकाम", "बांधकाम विभाग", "सार्वजनिक बांधकाम विभाग", "सा.बां. विभाग",
    ),
    "Water Resources Department": (
        "water resources", "irrigation department", "जलसंपदा", "जलसंपदा विभाग",
    ),
    "Urban Development Department": (
        "urban development", "नगर विकास", "नगरविकास", "नगर विकास विभाग",
    ),
    "Rural Development Department": (
        "rural development", "ग्रामविकास", "ग्राम विकास विभाग",
    ),
    "Revenue and Forest Department": (
        "revenue", "forest", "महसूल", "वन विभाग", "महसूल व वन विभाग",
    ),
    "Finance Department": (
        "finance", "वित्त", "वित्त विभाग",
    ),
}

ENTITY_WORDS = {
    "news": (
        "news", "article", "report", "बातमी", "बातम्या", "वृत्त",
    ),
    "project": (
        "project", "projects", "work", "works", "प्रकल्प", "योजना",
        "कामे", "काम", "विकास",
    ),
    "tender": (
        "tender", "tenders", "bid", "bids", "निविदा", "ई-निविदा",
    ),
    "scheme": (
        "scheme", "schemes", "योजना",
    ),
    "document": (
        "document", "documents", "gr", "government resolution", "order", "circular",
        "शासन निर्णय", "परिपत्रक", "अधिसूचना",
    ),
    "video": (
        "video", "videos", "transcript", "transcripts", "व्हिडिओ", "व्हिडियो",
    ),
}


def _contains(text: str, term: str) -> bool:
    if not text or not term:
        return False
    if re.fullmatch(r"[a-z0-9]+", term, re.I):
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.I) is not None
    return term.casefold() in text.casefold()


@dataclass
class ParsedQuery:
    raw: str
    intent: str = "search"
    keywords: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    entity_type: str | None = None
    department: str | None = None
    tender_numbers: list[str] = field(default_factory=list)
    contractor_names: list[str] = field(default_factory=list)
    schemes: list[str] = field(default_factory=list)
    amounts: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    general_keywords: list[str] = field(default_factory=list)
    keyword_groups: list[tuple[str, ...]] = field(default_factory=list, repr=False)
    location_terms: list[str] = field(default_factory=list, repr=False)

    def public(self) -> dict:
        return {
            "intent": self.intent,
            "keywords": self.keywords,
            "location": self.locations,
            "entity_type": self.entity_type,
            "department": self.department,
            "tender_numbers": self.tender_numbers,
            "contractor_names": self.contractor_names,
            "schemes": self.schemes,
            "amounts": self.amounts,
            "dates": self.dates,
            "general_keywords": self.general_keywords,
        }

    def highlight_terms(self) -> list[str]:
        terms = []
        for loc in self.locations:
            terms.append(loc)
            terms.extend(LOCATIONS.get(loc, ()))
        for kw in self.keywords:
            terms.append(kw)
        if self.entity_type:
            terms.append(self.entity_type)
            terms.extend(ENTITY_WORDS.get(self.entity_type, ()))
        for group in self.keyword_groups:
            terms.extend(group[:5])
        terms.extend(self.general_keywords)
        terms.extend(self.tender_numbers)
        terms.extend(self.schemes)
        terms.extend(self.contractor_names)
        return list(dict.fromkeys(term for term in terms if term and term.casefold() not in FILLER_WORDS))


def parse_query(value: str) -> ParsedQuery:
    raw = re.sub(r"\s+", " ", (value or "").strip())
    lower = raw.casefold()
    parsed = ParsedQuery(raw=raw)

    # 1. Locations
    for canonical, aliases in LOCATIONS.items():
        if any(_contains(lower, alias) for alias in aliases):
            parsed.locations.append(canonical)
            parsed.location_terms.extend(aliases)

    # 2. Departments
    for department, aliases in DEPARTMENTS.items():
        if any(_contains(lower, alias) for alias in aliases):
            parsed.department = department
            break

    # 3. Entity type and Intent
    for entity, terms in ENTITY_WORDS.items():
        if any(_contains(lower, term) for term in terms):
            parsed.entity_type = entity
            parsed.intent = f"find_{entity}s" if not entity.endswith("s") else f"find_{entity}"
            break

    # 4. Project Types / Keywords
    for name, terms in PROJECT_TYPES.items():
        if any(_contains(lower, term) for term in terms):
            display = list(terms[:3])
            parsed.keywords.extend(display)
            parsed.keyword_groups.append(terms)

    # 5. Specific entities: tender numbers, amounts, dates, contractors, schemes
    parsed.tender_numbers = re.findall(r"\b(?=[A-Z0-9/-]*\d)[A-Z]{2,}[A-Z0-9]*(?:[/.-][A-Z0-9]+){1,}\b", raw, re.I)
    parsed.amounts = re.findall(r"(?:₹|rs\.?|inr)?\s*\d[\d,.]*\s*(?:crore|lakh|million|billion|कोटी|लाख)", raw, re.I)
    parsed.dates = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|20\d{2})\b", raw)
    contractor = re.search(r"\bcontractor\s+(?:named\s+)?([\w&.' -]{3,50})", raw, re.I)
    if contractor:
        parsed.contractor_names = [contractor.group(1).strip()]
    scheme = re.search(r"([\w\u0900-\u097f -]{3,60})\s+(?:scheme|योजना)\b", raw, re.I)
    if scheme:
        candidate = re.sub(r"^(?:show|find|give|tell)\s+", "", scheme.group(1), flags=re.I).strip()
        if candidate and candidate.casefold() not in FILLER_WORDS:
            parsed.schemes = [candidate]

    # 6. General keywords excluding filler words and recognized concepts
    recognized = set(FILLER_WORDS)
    recognized.update(x.casefold() for terms in PROJECT_TYPES.values() for x in terms)
    recognized.update(x.casefold() for terms in LOCATIONS.values() for x in terms)
    recognized.update(x.casefold() for terms in DEPARTMENTS.values() for x in terms)
    recognized.update(x.casefold() for terms in ENTITY_WORDS.values() for x in terms)
    tokens = re.findall(r"[\w₹/-]+", raw, re.UNICODE)
    parsed.general_keywords = [
        token for token in tokens
        if len(token) > 2
        and token.casefold() not in recognized
        and not any(token in group for group in (parsed.tender_numbers, parsed.amounts, parsed.dates))
    ]
    if not parsed.keyword_groups and parsed.general_keywords:
        for token in parsed.general_keywords:
            parsed.keyword_groups.append((token,))
            parsed.keywords.append(token)

    parsed.keywords = list(dict.fromkeys(parsed.keywords))
    parsed.location_terms = list(dict.fromkeys(parsed.location_terms))
    return parsed


def score_record(item, parsed: ParsedQuery) -> tuple[float, dict]:
    title = item.title or ""
    body = item.text or ""
    district = getattr(item, "district", None) or ""
    c_type = getattr(item, "content_type", None) or ""
    metadata = " ".join(filter(None, [
        getattr(item, "department", None),
        getattr(item, "district", None),
        getattr(item, "publisher", None),
        getattr(item, "channel", None),
        getattr(item, "source", None),
    ]))
    full = f"{title}\n{metadata}\n{body}"
    title_lower, body_lower, full_lower = title.casefold(), body.casefold(), full.casefold()

    # Location hits
    loc_in_title = any(_contains(title_lower, term) for term in parsed.location_terms)
    loc_in_district = bool(parsed.locations and district in parsed.locations)
    loc_in_body = any(_contains(full_lower, term) for term in parsed.location_terms)
    loc_matched = loc_in_title or loc_in_district or loc_in_body

    # Keyword hits
    kw_in_title = any(any(_contains(title_lower, term) for term in group) for group in parsed.keyword_groups)
    kw_in_body = any(any(_contains(full_lower, term) for term in group) for group in parsed.keyword_groups)
    kw_hits = [group for group in parsed.keyword_groups if any(_contains(full_lower, term) for term in group)]

    # Intent / entity type match
    entity_terms = ENTITY_WORDS.get(parsed.entity_type or "", ())
    entity_hit = False
    if parsed.entity_type == "news":
        entity_hit = (c_type == "news_article") or (c_type == "youtube_transcript") or any(_contains(full_lower, t) for t in entity_terms)
    elif parsed.entity_type == "project":
        entity_hit = (c_type == "government_document") or any(_contains(full_lower, t) for t in entity_terms)
    elif parsed.entity_type == "video":
        entity_hit = (c_type == "youtube_transcript") or any(_contains(full_lower, t) for t in entity_terms)
    elif parsed.entity_type:
        entity_hit = any(_contains(full_lower, t) for t in entity_terms)

    # Department match
    department_hit = bool(
        parsed.department
        and (
            _contains(metadata, parsed.department)
            or any(_contains(full_lower, alias) for alias in DEPARTMENTS.get(parsed.department, ()))
        )
    )

    # Exact weighted scoring
    score = 0.0
    if entity_hit:
        score += 10.0
    if loc_in_title or loc_in_district:
        score += 6.0
    elif loc_in_body:
        score += 2.0

    if kw_in_title:
        score += 10.0
    elif kw_in_body:
        score += 4.0

    # Strong direct title topic match: BOTH location and keyword in title
    if kw_in_title and (loc_in_title or loc_in_district):
        score += 15.0
    elif loc_in_title or kw_in_title:
        score += 5.0

    if department_hit:
        score += 5.0
    if len(kw_hits) > 1:
        score += 4.0
    if kw_in_body and not kw_in_title:
        score += 2.0

    for exact in [*parsed.tender_numbers, *parsed.contractor_names, *parsed.schemes, *parsed.amounts, *parsed.dates]:
        if _contains(full_lower, exact):
            score += 10.0

    # Multi-concept verification:
    has_loc = bool(parsed.locations)
    has_kw = bool(parsed.keyword_groups)
    req_concepts = int(has_loc) + int(has_kw)
    matched_concepts = int(has_loc and loc_matched) + int(has_kw and bool(kw_hits))

    if req_concepts > 1:
        if matched_concepts == req_concepts:
            score += 10.0
        else:
            score = 0.0  # Require multi-concept match

    return round(score, 2), {
        "keyword_hit": bool(kw_hits),
        "location_hit": loc_matched,
        "required_concepts": req_concepts,
        "matched_concepts": matched_concepts,
    }


def make_snippet(text: str, terms: list[str], width: int = 370) -> str:
    if not text:
        return ""
    lower = text.casefold()
    positions = [lower.find(term.casefold()) for term in terms if term and lower.find(term.casefold()) >= 0]
    position = min(positions) if positions else 0
    start = max(0, position - 100)
    snip = text[start:start + width].strip()
    if start > 0:
        snip = "…" + snip
    if start + width < len(text):
        snip = snip + "…"
    return snip
