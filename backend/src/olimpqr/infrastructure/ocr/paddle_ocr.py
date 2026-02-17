"""PaddleOCR service for text recognition."""

import re
import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _pdf_bytes_to_image_bytes(pdf_bytes: bytes) -> Optional[bytes]:
    """Convert first page of a PDF to PNG image bytes.

    Uses pdf2image (poppler) if available, otherwise falls back to
    PyMuPDF (fitz).
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        # Render at 300 DPI
        pix = page.get_pixmap(dpi=300)
        png_bytes = pix.tobytes("png")
        doc.close()
        return png_bytes
    except ImportError:
        pass
    except Exception as e:
        logger.warning("PyMuPDF PDF conversion failed: %s", e)

    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=1)
        if images:
            from io import BytesIO
            buf = BytesIO()
            images[0].save(buf, format="PNG")
            return buf.getvalue()
    except ImportError:
        pass
    except Exception as e:
        logger.warning("pdf2image PDF conversion failed: %s", e)

    return None

# DPI of generated PDF sheets (ReportLab default is 72 dpi)
PDF_DPI = 72
# Typical scan DPI
SCAN_DPI = 300
# Conversion factor: mm -> pixels at scan DPI
MM_TO_PX = SCAN_DPI / 25.4


@dataclass
class OCRResult:
    """Result of OCR processing."""
    score: Optional[int]
    confidence: float
    raw_text: str


class PaddleOCRService:
    """Service for OCR text recognition using PaddleOCR."""

    def __init__(self, use_gpu: bool = False):
        """Initialize PaddleOCR engine.

        Args:
            use_gpu: Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu
        self._ocr = None  # lazy init

    def _get_ocr(self):
        """Lazy-initialize PaddleOCR (heavy import)."""
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                use_gpu=self.use_gpu,
                show_log=False,
            )
        return self._ocr

    def extract_score_from_image(
        self,
        image_bytes: bytes,
        score_field_x: int,
        score_field_y: int,
        score_field_width: int,
        score_field_height: int,
    ) -> OCRResult:
        """Extract score from the fixed score-field region of a scanned sheet.

        Coordinates are in millimetres and converted to pixels using ``SCAN_DPI``.

        Args:
            image_bytes: Raw image bytes (PNG / JPEG)
            score_field_x: X coordinate of score field (mm)
            score_field_y: Y coordinate of score field (mm)
            score_field_width: Width of score field (mm)
            score_field_height: Height of score field (mm)

        Returns:
            OCRResult with score, confidence and raw text
        """
        try:
            # 1. Decode image (try PDF conversion if regular decode fails)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                png_bytes = _pdf_bytes_to_image_bytes(image_bytes)
                if png_bytes:
                    np_arr = np.frombuffer(png_bytes, np.uint8)
                    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                return OCRResult(score=None, confidence=0.0, raw_text="Failed to decode image")

            # 2. Convert mm to pixel coordinates
            x_px = int(score_field_x * MM_TO_PX)
            y_px = int(score_field_y * MM_TO_PX)
            w_px = int(score_field_width * MM_TO_PX)
            h_px = int(score_field_height * MM_TO_PX)

            # Add safety margin (±10 %)
            margin_x = int(w_px * 0.1)
            margin_y = int(h_px * 0.1)

            x1 = max(0, x_px - margin_x)
            y1 = max(0, y_px - margin_y)
            x2 = min(image.shape[1], x_px + w_px + margin_x)
            y2 = min(image.shape[0], y_px + h_px + margin_y)

            # 3. Crop score region
            score_region = image[y1:y2, x1:x2]
            if score_region.size == 0:
                return OCRResult(score=None, confidence=0.0, raw_text="Score region empty")

            # 4. Preprocess
            preprocessed = self._preprocess_image(score_region)

            # 5. Run OCR
            ocr = self._get_ocr()
            results = ocr.ocr(preprocessed, cls=True)

            # 6. Collect text lines
            raw_texts: list[str] = []
            confidences: list[float] = []

            if results and results[0]:
                for line in results[0]:
                    text = line[1][0]
                    conf = float(line[1][1])
                    raw_texts.append(text)
                    confidences.append(conf)

            raw_text = " ".join(raw_texts) if raw_texts else ""
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # 7. Parse score
            score = self._parse_score(raw_text)

            logger.info("OCR result: score=%s, confidence=%.2f, raw='%s'", score, avg_confidence, raw_text)
            return OCRResult(score=score, confidence=avg_confidence, raw_text=raw_text)

        except Exception as e:
            logger.error("OCR extraction failed: %s", e, exc_info=True)
            return OCRResult(score=None, confidence=0.0, raw_text=f"Error: {str(e)}")

    def extract_qr_from_image(self, image_bytes: bytes) -> Optional[str]:
        """Extract QR code data from scanned image.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Decoded QR string, or None if not found
        """
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode

            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                png_bytes = _pdf_bytes_to_image_bytes(image_bytes)
                if png_bytes:
                    np_arr = np.frombuffer(png_bytes, np.uint8)
                    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                return None

            decoded = pyzbar_decode(image)
            for obj in decoded:
                if obj.type == "QRCODE":
                    return obj.data.decode("utf-8")

            return None
        except Exception as e:
            logger.error("QR extraction failed: %s", e, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _preprocess_image(image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy.

        Pipeline: grayscale → CLAHE contrast enhancement → Otsu binarization.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # CLAHE – adaptive histogram equalisation
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Otsu thresholding for binarisation
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    @staticmethod
    def _parse_score(text: str) -> Optional[int]:
        """Parse the first integer from OCR text.

        Args:
            text: Raw OCR text

        Returns:
            Parsed score, or None if not found
        """
        numbers = re.findall(r"\d+", text)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return None
        return None
