# backend/app/services/groq_ocr_service.py

import os
import base64
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image
from openai import OpenAI

from app.services.ocr_service import OCRService


class GroqOCRService(OCRService):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise Exception("GROQ_API_KEY not found in environment variables")

        # Groq uses an OpenAI-compatible client
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        # Vision-capable model name may change over time.
        # Update this if Groq changes supported models.
        self.model_name = "meta-llama/llama-4-scout-17b-16e-instruct"

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF by rendering each page as an image
        and sending the images to Groq.
        """

        project_root = os.getcwd()

        normalized_path = os.path.abspath(
            os.path.join(project_root, os.path.normpath(file_path))
        )

        print("Original path from DB:", file_path)
        print("Resolved absolute path:", normalized_path)
        print("File exists:", os.path.exists(normalized_path))

        if not os.path.exists(normalized_path):
            raise Exception(f"File does not exist: {normalized_path}")

        doc = fitz.open(normalized_path)

        if len(doc) == 0:
            raise Exception("PDF contains no pages")

        extracted_pages = []

        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")

            # Base64 encode image
            encoded = base64.b64encode(image_bytes).decode("utf-8")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract all readable text from this "
                                    "scanned answer sheet page. Preserve "
                                    "question order and formatting."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": (
                                        "data:image/png;base64,"
                                        + encoded
                                    )
                                }
                            }
                        ]
                    }
                ],
                temperature=0
            )

            page_text = (
                response.choices[0]
                .message
                .content
                .strip()
            )

            extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages)