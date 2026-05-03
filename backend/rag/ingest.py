from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from backend.utils.cleaners import clean_document_text
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class RawElement:
    text: str
    page_number: int | None = None
    style: str | None = None


@dataclass(slots=True)
class RawDocument:
    document_name: str
    source_path: str
    file_type: str
    elements: list[RawElement]

    def to_dict(self) -> dict:
        return {
            "document_name": self.document_name,
            "source_path": self.source_path,
            "file_type": self.file_type,
            "elements": [asdict(element) for element in self.elements],
        }


class DocumentIngestor:
    SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt"}

    def load_documents(self, raw_docs_dir: Path) -> list[RawDocument]:
        documents: list[RawDocument] = []
        for path in sorted(raw_docs_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
                continue
            documents.append(self._load_document(path))

        logger.info(
            "Loaded documents",
            extra={"extra_data": {"document_count": len(documents), "directory": str(raw_docs_dir)}},
        )
        return documents

    def _load_document(self, path: Path) -> RawDocument:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            elements = self._load_pdf(path)
        elif suffix == ".docx":
            elements = self._load_docx(path)
        elif suffix == ".txt":
            elements = self._load_txt(path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        document = RawDocument(
            document_name=path.name,
            source_path=str(path),
            file_type=suffix.lstrip("."),
            elements=elements,
        )
        logger.info(
            "Parsed document",
            extra={
                "extra_data": {
                    "document_name": document.document_name,
                    "file_type": document.file_type,
                    "element_count": len(document.elements),
                }
            },
        )
        return document

    def _load_pdf(self, path: Path) -> list[RawElement]:
        """
        Robust PDF extraction using 'unstructured' with 'ocr_only' strategy.
        Handles scanned images, electronic text, and PPTX conversions.
        Avoids 'onnxruntime' crashes by bypassing heavy AI layout models.
        """
        try:
            from unstructured.partition.pdf import partition_pdf
        except ImportError as exc:
            raise ImportError(
                "Install unstructured[pdf], opencv-python-headless, and pytesseract."
            ) from exc


        unstructured_elements = partition_pdf(
            filename=str(path),
            strategy="ocr_only",
            ocr_languages="eng",
            include_page_breaks=True,
            chunking_strategy=None,
        )

        elements: list[RawElement] = []
        for el in unstructured_elements:
            # Capture metadata for page numbering
            page_num = getattr(el.metadata, "page_number", None)
            
            # Skip physical page break elements but use them to track page_num
            if el.category == "PageBreak":
                continue

            # Clean the text using existing cleaner
            text = clean_document_text(el.text)
            if not text:
                continue

            # Extract the element category (e.g., 'Title', 'NarrativeText') 
            # to help the SmartChunker identify headings.
            style = el.category if hasattr(el, "category") else None

            # Split into blocks and preserve page/style metadata
            for block in self._split_into_blocks(text):
                elements.append(RawElement(
                    text=block, 
                    page_number=page_num, 
                    style=style
                ))
        return elements

    def _load_docx(self, path: Path) -> list[RawElement]:
        try:
            from docx import Document
        except ImportError as exc:
            raise ImportError("Install python-docx to ingest DOCX files.") from exc

        document = Document(str(path))
        elements: list[RawElement] = []
        for paragraph in document.paragraphs:
            text = clean_document_text(paragraph.text)
            if not text:
                continue
            style_name = paragraph.style.name if paragraph.style is not None else None
            elements.append(RawElement(text=text, page_number=None, style=style_name))
        return elements

    def _load_txt(self, path: Path) -> list[RawElement]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_document_text(text)
        return [RawElement(text=block) for block in self._split_into_blocks(cleaned)]

    @staticmethod
    def _split_into_blocks(text: str) -> Iterable[str]:
        if not text:
            return []
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
        if blocks:
            return blocks
        return [line.strip() for line in text.splitlines() if line.strip()]