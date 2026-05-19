from abc import ABC, abstractmethod


class OCRService(ABC):
    """
    Abstract base class for all OCR providers.
    Any OCR implementation (Gemini, Nougat, Qwen-VL, etc.)
    must implement the extract_text method.
    """

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document and return it as a string.
        """
        pass