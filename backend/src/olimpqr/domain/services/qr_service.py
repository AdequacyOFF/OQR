"""QR code generation service."""

import io
import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
import base64


class QRService:
    """Service for generating QR codes."""

    ERROR_CORRECTION_LEVELS = {
        "L": ERROR_CORRECT_L,  # ~7% error correction
        "M": ERROR_CORRECT_M,  # ~15% error correction
        "Q": ERROR_CORRECT_Q,  # ~25% error correction
        "H": ERROR_CORRECT_H,  # ~30% error correction
    }

    @classmethod
    def generate_qr_code(
        cls,
        data: str,
        error_correction: str = "H",
        box_size: int = 10,
        border: int = 4
    ) -> bytes:
        """Generate QR code image as PNG bytes.

        Args:
            data: Data to encode in QR code
            error_correction: Error correction level (L, M, Q, H)
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            PNG image bytes
        """
        if error_correction not in cls.ERROR_CORRECTION_LEVELS:
            raise ValueError(f"Неверный уровень коррекции ошибок: {error_correction}")

        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=cls.ERROR_CORRECTION_LEVELS[error_correction],
            box_size=box_size,
            border=border,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to PNG bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return img_bytes.getvalue()

    @classmethod
    def generate_qr_code_base64(
        cls,
        data: str,
        error_correction: str = "H",
        box_size: int = 10,
        border: int = 4
    ) -> str:
        """Generate QR code as base64-encoded PNG.

        Args:
            data: Data to encode in QR code
            error_correction: Error correction level (L, M, Q, H)
            box_size: Size of each box in pixels
            border: Border size in boxes

        Returns:
            Base64-encoded PNG string (for embedding in HTML/JSON)
        """
        qr_bytes = cls.generate_qr_code(data, error_correction, box_size, border)
        return base64.b64encode(qr_bytes).decode('utf-8')
