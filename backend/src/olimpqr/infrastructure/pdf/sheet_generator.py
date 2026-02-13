"""Answer sheet PDF generator with QR code."""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from ...domain.services import QRService
from ...config import settings


class SheetGenerator:
    """Generator for answer sheet PDFs with QR codes."""

    def __init__(self):
        self.qr_service = QRService()
        self.page_width, self.page_height = A4

    def generate_answer_sheet(
        self,
        competition_name: str,
        variant_number: int,
        sheet_token: str
    ) -> bytes:
        """Generate answer sheet PDF with QR code.

        Args:
            competition_name: Name of the competition
            variant_number: Test variant number
            sheet_token: Token for QR code (for linking scan to attempt)

        Returns:
            PDF file as bytes
        """
        # Create PDF in memory
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Draw header
        self._draw_header(c, competition_name, variant_number)

        # Draw QR code
        self._draw_qr_code(c, sheet_token)

        # Draw score field (fixed position for OCR)
        self._draw_score_field(c)

        # Draw answer fields
        self._draw_answer_fields(c)

        # Draw footer
        self._draw_footer(c)

        # Finalize PDF
        c.save()

        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()

    def _draw_header(
        self,
        c: canvas.Canvas,
        competition_name: str,
        variant_number: int
    ):
        """Draw header with competition info."""
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 30*mm,
            competition_name
        )

        c.setFont("Helvetica", 12)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 40*mm,
            f"Вариант {variant_number}"
        )

    def _draw_qr_code(self, c: canvas.Canvas, sheet_token: str):
        """Draw QR code in top right corner."""
        # Generate QR code
        qr_bytes = self.qr_service.generate_qr_code(
            sheet_token,
            error_correction=settings.qr_error_correction,
            box_size=8,
            border=2
        )

        # Save QR to temp buffer and wrap with ImageReader
        qr_buffer = BytesIO(qr_bytes)
        qr_image = ImageReader(qr_buffer)

        # Draw QR code (40mm x 40mm in top right)
        qr_x = self.page_width - 50*mm
        qr_y = self.page_height - 50*mm
        qr_size = 40*mm

        c.drawImage(
            qr_image,
            qr_x,
            qr_y,
            width=qr_size,
            height=qr_size,
            preserveAspectRatio=True
        )

        # Draw label
        c.setFont("Helvetica", 8)
        c.drawString(qr_x, qr_y - 5*mm, "Scan Code")

    def _draw_score_field(self, c: canvas.Canvas):
        """Draw score field in fixed position for OCR.

        CRITICAL: These coordinates must match OCR settings!
        """
        # Get coordinates from settings
        x = settings.ocr_score_field_x * mm
        y = self.page_height - (settings.ocr_score_field_y * mm)
        width = settings.ocr_score_field_width * mm
        height = settings.ocr_score_field_height * mm

        # Draw thick border for OCR detection
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.rect(x, y, width, height)

        # Draw label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y + height + 3*mm, "ИТОГОВЫЙ БАЛЛ:")

        # Draw instruction
        c.setFont("Helvetica", 8)
        c.drawString(
            x,
            y - 5*mm,
            "Напишите итоговый балл ПЕЧАТНЫМИ цифрами"
        )

        # Draw placeholder
        c.setFont("Courier-Bold", 24)
        c.setFillColor(colors.lightgrey)
        c.drawCentredString(
            x + width/2,
            y + 3*mm,
            "___"
        )
        c.setFillColor(colors.black)

    def _draw_answer_fields(self, c: canvas.Canvas):
        """Draw numbered answer fields."""
        start_y = self.page_height - 100*mm
        line_height = 8*mm
        num_questions = 20

        c.setFont("Helvetica", 10)

        for i in range(1, num_questions + 1):
            y = start_y - (i * line_height)

            # Question number
            c.drawString(20*mm, y, f"{i}.")

            # Answer line
            c.line(
                30*mm,
                y,
                self.page_width - 20*mm,
                y
            )

    def _draw_footer(self, c: canvas.Canvas):
        """Draw footer with instructions."""
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)

        footer_text = [
            "Инструкции:",
            "1. Отвечайте четко и разборчиво",
            "2. Укажите итоговый балл в специальном поле",
            "3. Не сгибайте и не пачкайте лист"
        ]

        y = 30*mm
        for line in footer_text:
            c.drawString(20*mm, y, line)
            y -= 4*mm

        c.setFillColor(colors.black)
