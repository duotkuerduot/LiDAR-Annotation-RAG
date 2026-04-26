from __future__ import annotations

import re
from typing import Iterable


REPEATED_HEADER_PATTERNS = (
    re.compile(r"^\s*page\s+\d+\s*(of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*confidential\s*$", re.IGNORECASE),
    re.compile(r"^\s*internal use only\s*$", re.IGNORECASE),
)

WHITESPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = WHITESPACE_RE.sub(" ", text)
    text = MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def strip_noise_lines(lines: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for raw_line in lines:
        line = normalize_whitespace(raw_line)
        if not line:
            continue
        if any(pattern.match(line) for pattern in REPEATED_HEADER_PATTERNS):
            continue
        cleaned.append(line)
    return cleaned


def clean_document_text(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(strip_noise_lines(lines))


def clean_query(text: str) -> str:
    text = normalize_whitespace(text)
    text = re.sub(r"[^\w\s\-/.:?]", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def tokenize_for_search(text: str) -> list[str]:
    lowered = clean_query(text).lower()
    return re.findall(r"[a-z0-9][a-z0-9_\-/.:]*", lowered)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "chunk"
