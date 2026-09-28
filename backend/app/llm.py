"""Groq LLM Integration Module for CoreScapper & RTI Multi-Agent System.

Provides high-speed inference for:
1. Investigation planning and query decomposition.
2. Sourced factual claim extraction from evidence packs.
3. Contradiction reasoning and analysis.
4. Statutory Section 6(1) RTI application generation.
5. Official response classification and closed-loop gap updates.
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("corescapper.llm")

# Load environment variable if present or read from .env
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PRIMARY_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_groq_llm(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    json_mode: bool = False,
    timeout: float = 20.0,
) -> str | None:
    """Invokes Groq LLM with automatic fallback and error handling."""
    api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    if not api_key:
        logger.warning("GROQ_API_KEY not configured. Falling back to heuristic engine.")
        return None

    selected_model = model or PRIMARY_MODEL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload: dict[str, Any] = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(GROQ_API_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return content.strip()
            else:
                logger.warning(f"Groq API returned {resp.status_code}: {resp.text}. Trying fallback model {FALLBACK_MODEL}...")
                payload["model"] = FALLBACK_MODEL
                fallback_resp = client.post(GROQ_API_URL, headers=headers, json=payload)
                if fallback_resp.status_code == 200:
                    data = fallback_resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                logger.error(f"Fallback model failed with status {fallback_resp.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}", exc_info=True)
        return None


def parse_json_from_llm(text: str | None) -> Any:
    """Safely extracts JSON from LLM response whether wrapped in markdown or raw."""
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    # Regex extract json block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try finding first { or [
    start_brace = text.find("{")
    start_bracket = text.find("[")
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        end_brace = text.rfind("}")
        if end_brace > start_brace:
            try:
                return json.loads(text[start_brace : end_brace + 1])
            except Exception:
                pass
    elif start_bracket != -1:
        end_bracket = text.rfind("]")
        if end_bracket > start_bracket:
            try:
                return json.loads(text[start_bracket : end_bracket + 1])
            except Exception:
                pass
    return None
