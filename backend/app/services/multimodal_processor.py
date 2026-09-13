import os
import logging
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.system_event import SystemEvent

logger = logging.getLogger(__name__)

@dataclass
class ExtractedPage:
    page_number: int
    text: str
    metadata: Dict[str, Any]

class OCRProvider:
    def is_available(self) -> bool:
        return False
    def extract_text_from_image(self, image_path: str) -> str:
        raise NotImplementedError()

class TesseractOCRProvider(OCRProvider):
    def __init__(self):
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self._available = True
        except ImportError:
            self._available = False

    def is_available(self) -> bool:
        if not self._available:
            return False
        import shutil
        return shutil.which("tesseract") is not None

    def extract_text_from_image(self, image_path: str) -> str:
        if not self.is_available():
            raise RuntimeError("OCR Provider (Tesseract) is unavailable.")
        from PIL import Image
        return self.pytesseract.image_to_string(Image.open(image_path))

class MultimodalProcessor:
    def __init__(self, db: Optional[Session] = None, ocr_provider: Optional[OCRProvider] = None):
        self.db = db
        self.ocr_provider = ocr_provider or TesseractOCRProvider()

    def _log_event(self, action: str, details: dict, status: str = "success"):
        if not self.db:
            return
        severity = "info" if status == "success" else "warning"
        event = SystemEvent(
            event_type="multimodal_processing",
            severity=severity,
            source="MultimodalProcessor",
            message=f"Multimodal processing {action}: {status}",
            metadata_=details
        )
        self.db.add(event)
        self.db.commit()

    def process_file(self, filepath: str, ext: str) -> List[ExtractedPage]:
        self._log_event("started", {"filepath": filepath, "extension": ext})
        try:
            if ext in ["txt", "md"]:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    pages = [ExtractedPage(page_number=1, text=f.read(), metadata={"source_type": "text"})]
            elif ext == "pdf":
                pages = self._process_pdf(filepath)
            elif ext in ["png", "jpg", "jpeg", "webp"]:
                pages = self._process_image(filepath)
            else:
                raise ValueError(f"Unsupported extension: {ext}")
                
            self._log_event("completed", {"filepath": filepath, "pages": len(pages)})
            return pages
        except Exception as e:
            self._log_event("failed", {"filepath": filepath, "error": str(e)}, status="failed")
            raise

    def _process_image(self, filepath: str) -> List[ExtractedPage]:
        if not self.ocr_provider.is_available():
            raise RuntimeError("OCR is requested for an image, but OCR provider is unavailable.")
        
        text = self.ocr_provider.extract_text_from_image(filepath)
        return [ExtractedPage(page_number=1, text=text, metadata={"source_type": "image", "ocr_used": True})]

    def _process_pdf(self, filepath: str) -> List[ExtractedPage]:
        pages = []
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(ExtractedPage(page_number=i+1, text=text, metadata={"source_type": "pdf_text"}))
                else:
                    if self.ocr_provider.is_available():
                        try:
                            import shutil
                            if shutil.which("pdftoppm") is None:
                                # pdf2image requires poppler (pdftoppm)
                                pages.append(ExtractedPage(page_number=i+1, text="", metadata={"source_type": "pdf_scanned_no_poppler"}))
                                continue
                                
                            from pdf2image import convert_from_path
                            images = convert_from_path(filepath, first_page=i+1, last_page=i+1)
                            if images:
                                with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                                    images[0].save(tmp.name, format="PNG")
                                    ocr_text = self.ocr_provider.extract_text_from_image(tmp.name)
                                    pages.append(ExtractedPage(page_number=i+1, text=ocr_text, metadata={"source_type": "pdf_ocr", "ocr_used": True}))
                            else:
                                pages.append(ExtractedPage(page_number=i+1, text="", metadata={"source_type": "pdf_empty"}))
                        except Exception as e:
                            logger.warning(f"Failed to OCR PDF page {i+1}: {e}")
                            pages.append(ExtractedPage(page_number=i+1, text="", metadata={"source_type": "pdf_failed_ocr", "error": str(e)}))
                    else:
                        pages.append(ExtractedPage(page_number=i+1, text="", metadata={"source_type": "pdf_scanned_no_ocr"}))
        except Exception as e:
            logger.error(f"Error processing PDF {filepath}: {e}")
            raise
        return pages
