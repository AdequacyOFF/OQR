"""Answer sheet PDF generator with QR code."""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ...domain.services import QRService
from ...config import settings


# Register fonts with Cyrillic support
try:
    # Try to register DejaVu fonts (included with reportlab)
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # DejaVu fonts are usually available in reportlab's fonts directory
    font_path = '/usr/share/fonts/truetype/dejavu/'
    if os.path.exists(font_path + 'DejaVuSans.ttf'):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path + 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path + 'DejaVuSans-Bold.ttf'))
    else:
        # Fallback to Helvetica (limited Cyrillic support)
        pass
except Exception as e:
    # If font registration fails, continue with default fonts
    print(f"Warning: Could not register custom fonts: {e}")


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

        # Draw logo in top left corner
        self._draw_logo(c)

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

    def _draw_logo(self, c: canvas.Canvas):
        """Draw logo in top left corner."""
        import os
        logo_path = os.path.join(os.path.dirname(__file__), 'logo_black.png')

        if os.path.exists(logo_path):
            try:
                logo_image = ImageReader(logo_path)
                # Draw logo (30mm x 30mm in top left)
                logo_x = 15*mm
                logo_y = self.page_height - 35*mm
                logo_size = 25*mm

                c.drawImage(
                    logo_image,
                    logo_x,
                    logo_y,
                    width=logo_size,
                    height=logo_size,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                # If logo fails to load, continue without it
                print(f"Warning: Could not load logo: {e}")

    def _draw_header(
        self,
        c: canvas.Canvas,
        competition_name: str,
        variant_number: int
    ):
        """Draw header with competition info."""
        # Use DejaVu font for Cyrillic support, fallback to Helvetica
        try:
            c.setFont("DejaVuSans-Bold", 18)
        except:
            c.setFont("Helvetica-Bold", 18)

        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 30*mm,
            "БЛАНК ОТВЕТОВ"
        )

        try:
            c.setFont("DejaVuSans", 12)
        except:
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

        # Draw label with Cyrillic support
        try:
            c.setFont("DejaVuSans-Bold", 10)
        except:
            c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y + height + 3*mm, "ИТОГОВЫЙ БАЛЛ:")

        # Draw instruction with Cyrillic support
        try:
            c.setFont("DejaVuSans", 8)
        except:
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
        """Draw large answer grid with notebook-style grid."""
        # Warning text with Cyrillic support
        try:
            c.setFont("DejaVuSans-Bold", 11)
        except:
            c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.red)
        warning_y = self.page_height - 60*mm  # Moved up by 30mm
        c.drawCentredString(
            self.page_width / 2,
            warning_y,
            "ВНИМАНИЕ! Заполняйте ответы строго внутри рамки"
        )
        c.setFillColor(colors.black)

        # Large rectangle frame - adjusted position and height
        frame_x = 20*mm
        frame_y = self.page_height - 240*mm - 20*mm  # Moved up by 30mm
        frame_width = self.page_width - 40*mm
        frame_height = 165*mm + 20*mm  # Increased by 20mm (2cm)

        # Draw thick outer border
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.rect(frame_x, frame_y, frame_width, frame_height)

        # Draw horizontal grid lines
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        line_spacing = 8*mm
        num_h_lines = int(frame_height / line_spacing)

        for i in range(1, num_h_lines):
            y = frame_y + (i * line_spacing)
            c.line(frame_x, y, frame_x + frame_width, y)

        # Draw vertical grid lines for proper grid
        col_spacing = 8*mm
        num_v_lines = int(frame_width / col_spacing)

        for i in range(1, num_v_lines):
            x = frame_x + (i * col_spacing)
            c.line(x, frame_y, x, frame_y + frame_height)

        c.setStrokeColor(colors.black)

    def _draw_footer(self, c: canvas.Canvas):
        """Draw footer with instructions (no signature field)."""
        try:
            c.setFont("DejaVuSans", 8)
        except:
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
