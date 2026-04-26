from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable

from backend.rag.ingest import RawDocument, RawElement
from backend.utils.cleaners import slugify

HEADING_STYLE_RE = re.compile(r"heading", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*(?:" + re.escape("\u2022") + r"|[-*]|\d+[.)]|[a-zA-Z][.)])\s+")
RULE_RE = re.compile(
    r"\b(must|should|shall|always|never|do not|don't|cannot|can not|required|only if)\b",
    re.IGNORECASE,
)
EXAMPLE_RE = re.compile(r"\b(example|for example|e\.g\.)\b", re.IGNORECASE)
DEFINITION_RE = re.compile(r"\b(definition|means|defined as|refers to)\b", re.IGNORECASE)
INSTRUCTION_RE = re.compile(r"\b(click|select|mark|label|annotate|draw|use|set)\b", re.IGNORECASE)


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    text: str
    document_name: str
    section_title: str
    chunk_type: str
    page_number: int | None

    def to_dict(self) -> dict:
        return asdict(self)


class SmartChunker:
    def chunk_documents(self, documents: Iterable[RawDocument]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for document in documents:
            chunks.extend(self._chunk_document(document))
        return chunks

    def _chunk_document(self, document: RawDocument) -> list[Chunk]:
        current_section = "General"
        buffer: list[RawElement] = []
        buffer_type: str | None = None
        chunks: list[Chunk] = []
        chunk_counter = 0

        def flush_buffer() -> None:
            nonlocal buffer, buffer_type, chunk_counter
            if not buffer:
                return
            text = "\n".join(element.text for element in buffer).strip()
            if not text:
                buffer = []
                buffer_type = None
                return
            first_page = next((element.page_number for element in buffer if element.page_number is not None), None)
            chunk_counter += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{slugify(document.document_name)}-{chunk_counter}",
                    text=text,
                    document_name=document.document_name,
                    section_title=current_section,
                    chunk_type=buffer_type or self._classify_chunk_type(text),
                    page_number=first_page,
                )
            )
            buffer = []
            buffer_type = None

        for element in document.elements:
            text = element.text.strip()
            if not text:
                continue
            if self._is_heading(text, element.style):
                flush_buffer()
                current_section = text
                continue

            element_type = self._classify_chunk_type(text)
            if self._should_force_new_chunk(text, element_type, buffer, buffer_type):
                flush_buffer()

            if BULLET_RE.match(text):
                flush_buffer()
                buffer = [element]
                buffer_type = element_type
                flush_buffer()
                continue

            if buffer and buffer_type and element_type != buffer_type:
                flush_buffer()

            buffer.append(element)
            buffer_type = element_type

            if self._is_complete_idea(text, element_type):
                flush_buffer()

        flush_buffer()
        return chunks

    @staticmethod
    def _is_heading(text: str, style: str | None) -> bool:
        if style and HEADING_STYLE_RE.search(style):
            return True
        stripped = text.strip(":")
        if len(stripped.split()) <= 10 and stripped == stripped.upper() and len(stripped) > 3:
            return True
        if len(stripped.split()) <= 8 and stripped.istitle():
            return True
        if text.endswith(":") and len(text.split()) <= 10:
            return True
        return False

    @staticmethod
    def _classify_chunk_type(text: str) -> str:
        if EXAMPLE_RE.search(text):
            return "example"
        if DEFINITION_RE.search(text):
            return "definition"
        if RULE_RE.search(text):
            return "rule"
        if INSTRUCTION_RE.search(text):
            return "instruction"
        return "instruction"

    @staticmethod
    def _should_force_new_chunk(
        text: str,
        element_type: str,
        buffer: list[RawElement],
        buffer_type: str | None,
    ) -> bool:
        if not buffer:
            return False
        if element_type != buffer_type:
            return True
        if BULLET_RE.match(text):
            return True
        if text.lower().startswith(("note:", "warning:", "exception:", "rule ", "example ")):
            return True
        if len("\n".join(item.text for item in buffer)) > 1800:
            return True
        return False

    @staticmethod
    def _is_complete_idea(text: str, chunk_type: str) -> bool:
        if BULLET_RE.match(text):
            return True
        if chunk_type in {"rule", "definition", "example"} and len(text) >= 120:
            return True
        if text.endswith((".", "!", "?")) and len(text) >= 220:
            return True
        return False
