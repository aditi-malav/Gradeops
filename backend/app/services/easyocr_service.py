# backend/app/services/easyocr_service.py

import os

import fitz  # PyMuPDF
import easyocr
from PIL import Image

from app.services.ocr_service import OCRService


class EasyOCRService(OCRService):
    def __init__(self):
        # gpu=False ensures it works on all systems.
        # Change to gpu=True if CUDA is available.
        self.reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF by rendering each page as an image
        and processing them locally using EasyOCR.
        """

        project_root = os.getcwd()

        normalized_path = os.path.abspath(
            os.path.join(project_root, os.path.normpath(file_path))
        )

        print("Original path from DB:", file_path)
        print("Resolved absolute path:", normalized_path)
        print("File exists:", os.path.exists(normalized_path))

        if not os.path.exists(normalized_path):
            raise Exception(
                f"File does not exist: {normalized_path}"
            )

        doc = fitz.open(normalized_path)

        if len(doc) == 0:
            raise Exception("PDF contains no pages")

        extracted_pages = []

        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")

            # EasyOCR accepts raw bytes directly
            results = self.reader.readtext(
                image_bytes,
                detail=0,
                paragraph=True
            )

            page_text = "\n".join(results).strip()

            extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages)