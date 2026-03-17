import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extract and join all text from a PDF file."""
    doc = fitz.open(file_path)
    pages_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text.strip())
    doc.close()

    full_text = "\n\n".join(pages_text)
    return full_text
