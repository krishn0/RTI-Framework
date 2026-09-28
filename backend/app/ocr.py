"""OCR Text Extraction Pipeline for Scanned PDFs and Gazette Images.

Supports English & Marathi (Devanagari) OCR with automatic scanned page detection.
"""
from __future__ import annotations

import io
import logging
from typing import Any

import fitz  # PyMuPDF
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    PYTESSERACT_AVAILABLE = False

from .marathi import normalize_marathi_pdf_text

logger = logging.getLogger("corescapper.ocr")


def is_scanned_page(text: str, min_chars: int = 40) -> bool:
    """Checks if a PDF page appears to be a scanned image with minimal/no extracted text."""
    clean = (text or "").strip()
    return len(clean) < min_chars


def ocr_pixmap(pix: fitz.Pixmap, lang: str = "mar+eng") -> str:
    """Performs OCR on a PyMuPDF page pixmap using pytesseract or PyMuPDF OCR."""
    # 1. Try pytesseract if available
    if PYTESSERACT_AVAILABLE:
        try:
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            # Try bilingual OCR first, fallback to english if marathi tessdata not on system
            try:
                raw_text = pytesseract.image_to_string(img, lang=lang)
            except Exception:
                raw_text = pytesseract.image_to_string(img, lang="eng")
            return normalize_marathi_pdf_text(raw_text)
        except Exception as e:
            logger.debug(f"Pytesseract OCR failed or tesseract binary not in PATH: {e}")

    # 2. Return empty if OCR binaries are unavailable
    return ""


def extract_page_text_with_ocr(page: fitz.Page, ocr_enabled: bool = True) -> str:
    """Extracts text from a single PDF page with automatic OCR fallback for scanned pages."""
    text = page.get_text("text") or ""
    normalized = normalize_marathi_pdf_text(text)

    if is_scanned_page(normalized) and ocr_enabled:
        try:
            # Render page at 2x resolution (144 dpi) for high OCR fidelity
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            ocr_text = ocr_pixmap(pix, lang="mar+eng")
            if len(ocr_text.strip()) > len(normalized.strip()):
                return ocr_text
        except Exception as e:
            logger.debug(f"OCR rendering error on page {page.number}: {e}")

    return normalized


def extract_pdf_pages_with_ocr(pdf_bytes: bytes, ocr_enabled: bool = True) -> list[str]:
    """Extracts all pages from PDF bytes, automatically running OCR on scanned pages."""
    extracted = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = extract_page_text_with_ocr(page, ocr_enabled=ocr_enabled)
            extracted.append(page_text)
    return extracted
