from app.services.groq_ocr_service import GroqOCRService
from app.services.openrouter_ocr_service import OpenRouterOCRService
from app.services.huggingface_ocr_service import HuggingFaceOCRService
from app.services.easyocr_service import EasyOCRService


class MultiOCRService:
    """
    Master OCR service that tries multiple providers in order.
    OCR succeeds as long as at least one provider is available.
    """

    def __init__(self):
        self.providers = [
            GroqOCRService(),
            OpenRouterOCRService(),
            HuggingFaceOCRService(),
            EasyOCRService(),   # Unlimited local fallback
        ]

    def extract_text(self, file_path: str) -> str:
        errors = []

        for provider in self.providers:
            provider_name = provider.__class__.__name__

            try:
                print(f"Trying OCR with {provider_name}...")

                extracted_text = provider.extract_text(file_path)

                if extracted_text and extracted_text.strip():
                    print(f"OCR succeeded using {provider_name}")
                    return extracted_text

                errors.append(
                    f"{provider_name}: returned empty text"
                )

            except Exception as e:
                print(f"OCR failed using {provider_name}: {e}")
                errors.append(
                    f"{provider_name}: {str(e)}"
                )

        raise Exception(
            "All OCR providers failed.\n\n"
            + "\n".join(errors)
        )