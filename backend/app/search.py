"""Structured query parsing and deterministic relevance scoring."""
import re
from dataclasses import dataclass, field


FILLER_WORDS = {
    "show", "find", "give", "tell", "me", "in", "the", "about", "information",
    "please", "all", "any", "for", "of", "on", "with", "from", "related",
    "to", "is", "are", "a", "an", "what", "which", "how", "list", "get", "details",
    "काय", "माहिती", "द्या", "दाखवा", "बघा",
}

# Common spelling typos mapped to standard canonical terms
TYPO_CORRECTIONS = {
    "constration": "construction",
    "constraction": "construction",
    "contruction": "construction",
    "costruction": "construction",
    "contarctor": "contractor",
    "contracter": "contractor",
    "contrator": "contractor",
    "tendor": "tender",
    "tendur": "tender",
    "budjet": "budget",
    "goverment": "government",
    "govrnment": "government",
    "departmnt": "department",
    "resoluton": "resolution",
    "resalution": "resolution",
    "coridor": "corridor",
    "flyovr": "flyover",
    "flyovur": "flyover",
    "expresway": "expressway",
    "expresswy": "expressway",
    "maharastra": "maharashtra",
    "samruddhi": "samruddhi",
    "samrudhi": "samruddhi",
    "hghway": "highway",
    "higway": "highway",
    "widning": "widening",
    "pothols": "potholes",
    "pot holes": "potholes",
}

ALLOWED_SHORT_TOKENS = {
    "nh", "sh", "gr", "cr", "boq", "nit", "rfp", "pi", "ml", "km",
    "pwd", "mc", "bmc", "pmc", "nmmc", "pcmc", "mmrda", "cidco", "msrdc", "nhai", "wr", "ud"
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
        "road", "roads", "road project", "roadwork", "roadworks", "road construction",
        "highway", "highways", "national highway", "national highways", "state highway", "state highways",
        "nh", "sh", "msh", "nhai", "expressway", "expressways", "corridor", "freeway",
        "bridge", "bridges", "flyover", "flyovers", "street", "streets", "bypass",
        "widening", "asphalt", "asphalting", "tarring", "pothole", "potholes", "concreting",
        "रस्ता", "रस्ते", "रस्त्यांचा", "रस्त्यांची", "रस्त्यांचे", "रस्त्याचा",
        "रस्त्याची", "रस्त्यासाठी", "रस्त्यांवर", "रस्त्यावर", "रस्त्यांच्या",
        "मार्ग", "महामार्ग", "राष्ट्रीय महामार्ग", "राज्य महामार्ग", "द्रुतगती मार्ग",
        "समृद्धी महामार्ग", "पूल", "सड़क", "सड़कें", "सड़कों", "सड़क", "सड़कें", "सड़कों",
        "फ्लाईओव्हर", "उड्डाणपूल", "पाणंद रस्ता", "पाणंद", "डांबरीकरण", "काँक्रीटीकरण",
        "रस्ता बांधकाम", "रस्ते रुंदीकरण", "खड्डे", "रस्ता दुरुस्ती", "बायपास",
    ),
    "metro": (
        "metro", "metro project", "metro rail", "metro train", "मेट्रो",
        "मेट्रो प्रकल्प", "मेट्रो विस्तार", "मेट्रो मार्ग", "मेट्रो रेल्वे",
    ),
    "water": (
        "water", "water supply", "irrigation", "dam", "dams", "jal", "pipeline", "canal", "drinking water",
        "जल", "पाणी", "पाणीपुरवठा", "सिंचन", "धरण", "धरणे", "जलसंपदा", "कालवा", "पाईपलाईन", "पिण्याचे पाणी",
    ),
    "housing": (
        "housing", "housing project", "pradhan mantri awas", "mhada", "slum", "sra",
        "घरकुल", "गृहनिर्माण", "म्हाडा", "घरकुले", "आवास", "झोपडपट्टी",
    ),
    "railway": (
        "railway", "railways", "rail project", "train", "station", "bullet train",
        "रेल्वे", "रेल्वे प्रकल्प", "रेल्वे मार्ग", "रेल्वे सेवा", "स्थानक", "बुलेट ट्रेन",
    ),
    "health": (
        "health", "hospital", "hospitals", "medical", "clinic", "oxygen", "medicine", "doctor",
        "ambulance", "phc", "aarogya", "beds", "icu",
        "आरोग्य", "रुग्णालय", "दवाखाना", "वैद्यकीय", "औषध", "डॉक्टर", "आरोग्य विभाग", "प्राथमिक आरोग्य केंद्र", "रुग्ण",
    ),
    "education": (
        "education", "school", "schools", "college", "colleges", "university", "student", "students",
        "grant", "scholarship", "teacher", "smart classroom", "shikshan",
        "शिक्षण", "शाळा", "महाविद्यालय", "विद्यापीठ", "विद्यार्थी", "शिक्षक", "अनुदान", "शिष्यवृत्ती", "शालेय",
    ),
    "energy": (
        "energy", "power", "electricity", "solar", "mseb", "mahadiscom", "transformer", "grid", "substation",
        "ऊर्जा", "वीज", "विद्युत", "सौरऊर्जा", "महावितरण", "सौर",
    ),
    "agriculture": (
        "agriculture", "farming", "farmer", "farmers", "crop", "loan waiver", "subsidy", "krishi", "fertilizer", "seeds",
        "कृषी", "शेतकरी", "पिक", "कर्जमाफी", "अनुदान", "खते", "बियाणे", "कृषी विभाग",
    ),
    "sanitation": (
        "sanitation", "cleanliness", "waste", "garbage", "drainage", "sewage", "swachh",
        "स्वच्छता", "कचरा", "सांडपाणी", "ड्रेनेज", "स्वच्छ भारत",
    ),
    "transport": (
        "transport", "bus", "buses", "msrtc", "depot", "st bus", "airport", "traffic",
        "परिवहन", "एसटी", "बस", "आगार", "विमानतळ", "वाहतूक", "एसटी महामंडळ",
    ),
    "municipal": (
        "municipal", "corporation", "municipality", "smart city", "ward", "mahanagarpalika", "nagarpalika", "zila parishad", "zp",
        "महानगरपालिका", "मनपा", "नगरपालिका", "स्मार्ट सिटी", "जिल्हा परिषद", "ग्रामपंचायत",
    ),
    "infrastructure": (
        "infrastructure", "development", "construction", "civil work", "civil works",
        "पायाभूत सुविधा", "नागरी विकास", "विकास कामे", "विकास", "बुनियादी ढांचा", "बांधकाम",
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
        "urban development", "nagar vikas", "नगर विकास", "नगरविकास", "नगर विकास विभाग",
    ),
    "Rural Development Department": (
        "rural development", "gram vikas", "ग्रामविकास", "ग्राम विकास विभाग",
    ),
    "Public Health Department": (
        "public health", "health department", "phd", "सार्वजनिक आरोग्य", "आरोग्य विभाग", "सार्वजनिक आरोग्य विभाग",
    ),
    "School Education and Sports Department": (
        "school education", "education department", "शालेय शिक्षण", "शिक्षण विभाग", "शालेय शिक्षण व क्रीडा विभाग",
    ),
    "Energy Department": (
        "energy department", "power department", "ऊर्जा विभाग",
    ),
    "Agriculture Department": (
        "agriculture department", "krishi vibhag", "कृषी विभाग",
    ),
    "Transport Department": (
        "transport department", "परिवहन विभाग",
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
        "project", "projects", "work", "works", "construction", "प्रकल्प", "योजना",
        "कामे", "काम", "विकास", "बांधकाम",
    ),
    "tender": (
        "tender", "tenders", "bid", "bids", "contract", "contractor", "e-tender",
        "निविदा", "ई-निविदा", "कंत्राट", "ठेकेदार",
    ),
    "scheme": (
        "scheme", "schemes", "योजना", "अभियान",
    ),
    "document": (
        "document", "documents", "gr", "government resolution", "order", "circular", "notification",
        "शासन निर्णय", "परिपत्रक", "अधिसूचना", "आदेश",
    ),
    "video": (
        "video", "videos", "transcript", "transcripts", "speech", "press conference", "debate",
        "व्हिडिओ", "व्हिडियो", "भाषण", "पत्रकार परिषद",
    ),
}


def _contains(text: str, term: str) -> bool:
    if not text or not term:
        return False
    if re.fullmatch(r"[a-z0-9]+", term, re.I):
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.I) is not None
    return term.casefold() in text.casefold()


def normalize_query_text(text: str) -> str:
    """Normalize common typos in search query while preserving casing and original tokens."""
    result = text
    for typo, correction in TYPO_CORRECTIONS.items():
        pattern = rf"\b{re.escape(typo)}\b"
        result = re.sub(pattern, correction, result, flags=re.I)
    return result


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
    # Apply spelling / typo normalization on the working copy
    normalized_raw = normalize_query_text(raw)
    lower = normalized_raw.casefold()
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

    # 4. Project Types / Domain Keywords
    for name, terms in PROJECT_TYPES.items():
        if any(_contains(lower, term) for term in terms):
            display = list(terms[:3])
            parsed.keywords.extend(display)
            parsed.keyword_groups.append(terms)

    # 5. Highway codes and numbers (e.g. NH-48, NH 66, SH 10, MSH-3)
    highways = re.findall(r"\b(?:NH|SH|MSH)[ -]?\d+\b", raw, re.I)
    if highways:
        for hw in highways:
            clean_hw = hw.upper().replace(" ", "-")
            parsed.general_keywords.append(hw)
            parsed.keywords.append(clean_hw)
            if PROJECT_TYPES["road"] not in parsed.keyword_groups:
                parsed.keyword_groups.append(PROJECT_TYPES["road"])
                parsed.keywords.extend(PROJECT_TYPES["road"][:3])

    # 6. Specific entities: tender numbers, amounts, dates, contractors, schemes
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

    # 7. General keywords: extract all meaningful query tokens
    recognized = set(FILLER_WORDS)
    recognized.update(x.casefold() for terms in LOCATIONS.values() for x in terms)
    
    tokens = re.findall(r"[\w\u0900-\u097f₹/-]+", normalized_raw, re.UNICODE)
    parsed.general_keywords = list(dict.fromkeys([
        token for token in tokens
        if (len(token) > 2 or token.casefold() in ALLOWED_SHORT_TOKENS or re.match(r"\d+", token))
        and token.casefold() not in recognized
        and not any(token in group for group in (parsed.tender_numbers, parsed.amounts, parsed.dates))
    ]))

    # CRITICAL: Always ensure all general query tokens participate in keyword groups and keywords!
    for token in parsed.general_keywords:
        token_lower = token.casefold()
        # Avoid duplicate single-word groups if already covered
        already_covered = any(token_lower in (t.casefold() for t in grp) for grp in parsed.keyword_groups)
        if not already_covered:
            parsed.keyword_groups.append((token, token_lower))
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
    kw_in_title_count = 0
    kw_in_body_count = 0
    kw_hits = []

    for group in parsed.keyword_groups:
        hit_title = any(_contains(title_lower, term) for term in group)
        hit_body = any(_contains(full_lower, term) for term in group)
        if hit_title:
            kw_in_title_count += 1
            kw_hits.append(group)
        elif hit_body:
            kw_in_body_count += 1
            kw_hits.append(group)

    # Intent / entity type match
    score = 0.0
    entity_terms = ENTITY_WORDS.get(parsed.entity_type or "", ())
    
    if parsed.entity_type == "news":
        if c_type == "news_article":
            score += 15.0
        elif c_type == "youtube_transcript":
            score += 4.0
        elif any(_contains(full_lower, t) for t in entity_terms):
            score += 5.0
    elif parsed.entity_type in {"project", "document", "tender"}:
        if c_type == "government_document":
            score += 15.0
        elif any(_contains(full_lower, t) for t in entity_terms):
            score += 6.0
    elif parsed.entity_type == "video":
        if c_type == "youtube_transcript":
            score += 15.0
        elif any(_contains(full_lower, t) for t in entity_terms):
            score += 5.0
    elif parsed.entity_type and any(_contains(full_lower, t) for t in entity_terms):
        score += 8.0

    # Department match
    department_hit = bool(
        parsed.department
        and (
            _contains(metadata, parsed.department)
            or any(_contains(full_lower, alias) for alias in DEPARTMENTS.get(parsed.department, ()))
        )
    )

    # Location scoring
    if loc_in_title:
        score += 10.0
    elif loc_in_district:
        score += 6.0
    elif loc_in_body:
        score += 2.0

    # Keyword scoring
    if kw_in_title_count > 0:
        score += 14.0 * kw_in_title_count
    if kw_in_body_count > 0:
        score += 4.0 * kw_in_body_count

    # Strong direct title match (location + keyword directly in title)
    if (loc_in_title or loc_in_district) and kw_in_title_count > 0:
        score += 22.0

    if department_hit:
        score += 8.0

    for exact in [*parsed.tender_numbers, *parsed.contractor_names, *parsed.schemes, *parsed.amounts, *parsed.dates]:
        if _contains(full_lower, exact):
            score += 12.0

    # Multi-concept verification
    has_loc = bool(parsed.locations)
    has_kw = bool(parsed.keyword_groups)
    req_concepts = int(has_loc) + int(has_kw)
    matched_concepts = int(has_loc and loc_matched) + int(has_kw and bool(kw_hits))

    if req_concepts > 1 and matched_concepts == req_concepts:
        score += 15.0

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
    
    # Find positions of all matched terms
    positions = []
    for term in sorted(terms, key=len, reverse=True):
        if not term or len(term) < 2:
            continue
        idx = lower.find(term.casefold())
        if idx >= 0:
            positions.append(idx)

    position = min(positions) if positions else 0
    start = max(0, position - 80)
    
    # Align to nearest word boundary
    if start > 0:
        prev_space = text.rfind(" ", max(0, start - 30), start + 10)
        if prev_space != -1:
            start = prev_space + 1

    end = min(len(text), start + width)
    if end < len(text):
        next_space = text.find(" ", end - 15, min(len(text), end + 30))
        if next_space != -1:
            end = next_space

    snip = text[start:end].strip()
    if start > 0:
        snip = "…" + snip
    if end < len(text):
        snip = snip + "…"
    return snip

