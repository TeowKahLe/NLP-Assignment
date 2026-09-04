
from pathlib import Path
import io

import pymupdf
from docx import Document
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

SUPPORTED_IMAGE_TYPES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".webp"
}


def extract_text_from_pdf(file_path):
    text = ""

    pdf = pymupdf.open(file_path)

    for page in pdf:
        page_text = page.get_text("text")

        if page_text:
            text += page_text + "\n"

    pdf.close()

    # If normal PDF text exists, use direct extraction
    if text.strip():
        return text.strip(), "PDF Text Extraction"

    # If no text is detected, use OCR
    return extract_text_from_scanned_pdf(file_path)


def extract_text_from_scanned_pdf(file_path):
    text = ""

    pdf = pymupdf.open(file_path)

    for page in pdf:
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2)
        )

        image_bytes = pix.tobytes("png")

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        page_text = pytesseract.image_to_string(
            image
        )

        text += page_text + "\n"

    pdf.close()

    return text.strip(), "OCR"


def extract_text_from_docx(file_path):
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(
                paragraph.text
            )

    text = "\n".join(paragraphs)

    return text.strip(), "DOCX Text Extraction"


def extract_text_from_image(file_path):
    image = Image.open(file_path)

    text = pytesseract.image_to_string(
        image
    )

    return text.strip(), "OCR"


def extract_text(file_path):
    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(
            file_path
        )

    elif extension == ".docx":
        return extract_text_from_docx(
            file_path
        )

    elif extension in SUPPORTED_IMAGE_TYPES:
        return extract_text_from_image(
            file_path
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


if __name__ == "__main__":
    print("Document processor ready.")