"""
PDF text extraction with accurate page tracking.
Fallback chain: pdfplumber → pypdf → raw bytes decode
"""
import io
from typing import Optional


def extract_text_with_pages(contents: bytes, filename: str) -> list[dict]:
    """
    Returns list of {page_number, text} dicts.
    Each page is kept separate so citation page numbers are exact.
    """
    suffix = filename.lower().split(".")[-1] if "." in filename else ""

    if suffix in ("pdf",):
        result = _try_pdfplumber(contents)
        if result:
            return result
        result = _try_pypdf(contents)
        if result:
            return result

    # Fallback: treat as plain text, split on form feeds or double newlines
    try:
        text = contents.decode("utf-8", errors="ignore")
    except Exception:
        text = contents.decode("latin-1", errors="ignore")

    pages = text.split("\f")  # form feed = page break in some text dumps
    if len(pages) <= 1:
        # No form feeds — split into ~3000-char synthetic pages
        pages = [text[i:i+3000] for i in range(0, len(text), 3000)]

    return [{"page_number": i + 1, "text": p.strip()} for i, p in enumerate(pages) if p.strip()]


def _try_pdfplumber(contents: bytes) -> Optional[list[dict]]:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                # Also extract tables as text
                for table in (page.extract_tables() or []):
                    for row in table:
                        row_text = " | ".join(str(cell or "").strip() for cell in row)
                        if row_text.strip(" |"):
                            text += "\n" + row_text
                if text.strip():
                    pages.append({"page_number": i + 1, "text": text.strip()})
        return pages if pages else None
    except Exception:
        return None


def _try_pypdf(contents: bytes) -> Optional[list[dict]]:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(contents))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page_number": i + 1, "text": text.strip()})
        return pages if pages else None
    except Exception:
        return None


def pages_to_chunks(pages: list[dict], chunk_size: int = 3000) -> list[dict]:
    """
    Merge pages into chunks of ~chunk_size chars.
    Each chunk tracks page_start and page_end for citation.
    """
    chunks = []
    current_text = ""
    current_page_start = pages[0]["page_number"] if pages else 1
    current_page_end = current_page_start

    for page in pages:
        page_text = page["text"]
        page_num = page["page_number"]

        if len(current_text) + len(page_text) > chunk_size and current_text:
            chunks.append({
                "text": current_text.strip(),
                "page_start": current_page_start,
                "page_end": current_page_end,
            })
            current_text = page_text
            current_page_start = page_num
            current_page_end = page_num
        else:
            current_text += "\n\n" + page_text
            current_page_end = page_num

    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "page_start": current_page_start,
            "page_end": current_page_end,
        })

    return chunks
