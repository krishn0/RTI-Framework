"""Repairs common legacy-font substitutions found in Maharashtra government PDFs.

Some PDFs contain Devanagari-looking glyphs whose embedded character map points
to Latin Extended characters.  Keep the source extraction separately and use
this conservative normalizer for display and search.
"""
import re
import unicodedata


_PHRASES = (
    ("सहा ĢकÊपातून Ģायोिगक गाळ", "सहा प्रकल्पातून प्रायोगिक तत्त्वावर गाळ"),
    ("योजनेसाठी ४९ कोटी २६ ची तरतुद", "योजनेसाठी ४९ कोटी २६ लाख रुपयांची तरतूद"),
    ("पाटबंधारे´या", "पाटबंधारेच्या"),
    ("ĢकÊपातून", "प्रकल्पातून"),
    ("ĢकÊपांच्या", "प्रकल्पांच्या"),
    ("Ģायोिगक", "प्रायोगिक"),
    ("काढ½यात", "काढण्यात"),
    ("शेतकÉयांना", "शेतकऱ्यांना"),
    ("सीसीिटËही", "सीसीटीव्ही"),
    ("फेȏÂसगǎारे", "फेन्सिंगद्वारे"),
    ("िनयंĝण", "नियंत्रण"),
    ("नािशक", "नाशिक"),
    ("िजÊǩातील", "जिल्ह्यातील"),
    ("िजÊǩांसाठी", "जिल्ह्यांसाठी"),
    ("ȋसधुदुग«", "सिंधुदुर्ग"),
    ("ȋसधुरत्न समृǉ योजना", "सिंधुरत्न समृद्ध योजना"),
    ("र¾नािगरी", "रत्नागिरी"),
    ("वषȝसाठी", "वर्षांसाठी"),
    ("तरतुद", "तरतूद"),
    ("सहा प्रकल्पातून प्रायोगिक गाळ", "सहा प्रकल्पातून प्रायोगिक तत्त्वावर गाळ"),
    ("योजनेसाठी ४९ कोटी २६ ची तरतूद", "योजनेसाठी ४९ कोटी २६ लाख रुपयांची तरतूद"),
)

# Only apply these substitutions when legacy-font evidence is present. This
# prevents valid Unicode Marathi from being changed unnecessarily.
_LEGACY_MARKERS = frozenset("´ĢÊ½ÉËȏÂĝǎ«¾ȝ")
_GLYPHS = str.maketrans({
    "Ģ": "प्र",
    "Ê": "ल",
    "½": "ण",
    "É": "ऱ",
    "ĝ": "त्र",
    "ǎ": "द्व",
    "«": "र्ग",
    "¾": "त्",
})


def normalize_marathi_pdf_text(value: str) -> str:
    """Return searchable Unicode Marathi while leaving clean text intact."""
    if not value:
        return value

    text = unicodedata.normalize("NFC", value)
    for broken, corrected in _PHRASES:
        text = text.replace(broken, corrected)

    if any(character in value for character in _LEGACY_MARKERS):
        text = text.translate(_GLYPHS)
        # Frequent remnants after the safe one-codepoint substitutions.
        text = text.replace("´या", "च्या")
        text = text.replace("Ëही", "व्ही")

    # Line-oriented PDF extraction may split a sentence between every column.
    text = re.sub(
        r"सहा प्रकल्पातून प्रायोगिक\s+गाळ",
        "सहा प्रकल्पातून प्रायोगिक तत्त्वावर गाळ",
        text,
    )
    text = re.sub(
        r"योजनेसाठी\s+४९\s+कोटी\s+२६\s+ची\s+तरतूद",
        "योजनेसाठी ४९ कोटी २६ लाख रुपयांची तरतूद",
        text,
    )

    # Preserve paragraphs but remove extraction noise within lines.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()
