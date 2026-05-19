import os
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image

from app.services.ocr_service import OCRService
from app.services.gemini_client import get_gemini_model


class GeminiOCRService(OCRService):
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF by rendering each page as an image
        and sending the images to Gemini.
        """

    
        # Resolve the path relative to the project root directory
        # Example:
        # file_path from DB: "uploads\\abc.pdf"
        # absolute path: C:\Users\Aditi\Desktop\GradeOps\uploads\abc.pdf
    
        project_root = os.getcwd()

        normalized_path = os.path.abspath(
            os.path.join(project_root, os.path.normpath(file_path))
        )

        print("Original path from DB:", file_path)
        print("Resolved absolute path:", normalized_path)
        print("File exists:", os.path.exists(normalized_path))

        # Ensure the file exists
        if not os.path.exists(normalized_path):
            raise Exception(
                f"File does not exist: {normalized_path}"
            )

        
        # Open the PDF
     
        doc = fitz.open(normalized_path)

        if len(doc) == 0:
            raise Exception("PDF contains no pages")

      
        # Get configured Gemini model
       
        model = get_gemini_model()

        # Prompt + page images
        contents = [
            (
                "Extract all readable text from these scanned answer sheets. "
                "Preserve question order and formatting as clearly as possible."
            )
        ]

        # Convert each page to a PIL image
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            image = Image.open(BytesIO(image_bytes))
            contents.append(image)

  
        # Send to Gemini
    
        response = model.generate_content(contents)

        # Return extracted text

        return response.text.strip()