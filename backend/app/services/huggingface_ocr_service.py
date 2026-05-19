# backend/app/services/huggingface_ocr_service.py

import os

import fitz  # PyMuPDF
from PIL import Image
from huggingface_hub import InferenceClient

from app.services.ocr_service import OCRService


class HuggingFaceOCRService(OCRService):
    def __init__(self):
        api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not api_key:
            raise Exception(
                "HUGGINGFACE_API_KEY not found in environment variables"
            )

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=api_key
        )

        # OCR-focused model
        self.model_name = "microsoft/trocr-base-printed"

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF by rendering each page as an image
        and sending the images to Hugging Face Inference.
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

            # text_to_image returns OCR text for supported OCR models
            page_text = self.client.image_to_text(
                image_bytes,
                model=self.model_name
            )

            if isinstance(page_text, dict):
                page_text = page_text.get("generated_text", "")

            page_text = str(page_text).strip()

            extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages)