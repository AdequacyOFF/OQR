"""Badge PDF generator for participant QR badges."""

from dataclasses import dataclass
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from ...domain.services import QRService
from .sheet_generator import _register_fonts, _FONT_REGULAR, _FONT_BOLD


@dataclass
class BadgeData:
    """Data for a single badge."""
    name: str
    school: str
    institution: str
    qr_token: str


class BadgeGenerator:
    """Generator for participant badge PDFs with QR codes."""

    # Badge dimensions (3x3 grid on A4)
    COLS = 3
    ROWS = 3
    BADGES_PER_PAGE = 9

    # A4 page
    PAGE_W, PAGE_H = A4

    # Margins
    MARGIN_X = 10 * mm
    MARGIN_Y = 10 * mm

    # Badge size (calculated to fit 3x3 on A4 with margins)
    BADGE_W = (PAGE_W - 2 * MARGIN_X) / COLS   # ~63.3mm
    BADGE_H = (PAGE_H - 2 * MARGIN_Y) / ROWS   # ~92.3mm

    # QR size inside badge
    QR_SIZE = 30 * mm

    def __init__(self):
        _register_fonts()
        self.qr_service = QRService()

    def generate_badges_pdf(
        self,
        competition_name: str,
        badges: list[BadgeData],
    ) -> bytes:
        """Generate a PDF with badges grouped by institution.

        Args:
            competition_name: Name of the competition
            badges: List of badge data, pre-sorted by institution then name

        Returns:
            PDF file as bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Group badges by institution
        groups: dict[str, list[BadgeData]] = {}
        for badge in badges:
            key = badge.institution or "Без учреждения"
            groups.setdefault(key, []).append(badge)

        # Sort groups alphabetically
        sorted_institutions = sorted(groups.keys())

        badge_index = 0  # position on current page (0..8)
        first_page = True

        for institution in sorted_institutions:
            group_badges = groups[institution]

            # Start new page for each institution group
            if not first_page:
                c.showPage()
                badge_index = 0
            first_page = False

            # Draw institution header at top of page
            self._draw_institution_header(c, institution, competition_name)

            for badge in group_badges:
                if badge_index >= self.BADGES_PER_PAGE:
                    c.showPage()
                    badge_index = 0
                    self._draw_institution_header(c, institution, competition_name)

                col = badge_index % self.COLS
                row = badge_index // self.COLS

                # Badge origin (bottom-left corner)
                x = self.MARGIN_X + col * self.BADGE_W
                # Offset rows down to leave room for header
                header_offset = 15 * mm
                y = self.PAGE_H - self.MARGIN_Y - header_offset - (row + 1) * self.BADGE_H

                self._draw_badge(c, x, y, badge, competition_name)
                badge_index += 1

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    def _draw_institution_header(
        self, c: canvas.Canvas, institution: str, competition_name: str
    ):
        """Draw institution name header at top of page."""
        c.setFont(_FONT_BOLD, 11)
        c.drawCentredString(
            self.PAGE_W / 2,
            self.PAGE_H - self.MARGIN_Y - 5 * mm,
            f"{competition_name} — {institution}",
        )

    def _draw_badge(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        badge: BadgeData,
        competition_name: str,
    ):
        """Draw a single badge at the given position."""
        w = self.BADGE_W
        h = self.BADGE_H
        pad = 3 * mm

        # Dashed cut-line border
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        c.rect(x, y, w, h)
        c.setDash()  # reset

        # Inner content area
        cx = x + w / 2  # center x
        top = y + h - pad

        # Logo
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "logo_black.png")
        if os.path.exists(logo_path):
            try:
                logo_size = 12 * mm
                logo_image = ImageReader(logo_path)
                c.drawImage(
                    logo_image,
                    cx - logo_size / 2,
                    top - logo_size,
                    width=logo_size,
                    height=logo_size,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                top -= logo_size + 2 * mm
            except Exception:
                pass

        # "OlimpQR" title
        c.setFont(_FONT_BOLD, 9)
        c.drawCentredString(cx, top - 3 * mm, "OlimpQR")
        top -= 7 * mm

        # Competition name (smaller)
        c.setFont(_FONT_REGULAR, 6)
        comp_text = competition_name
        if len(comp_text) > 30:
            comp_text = comp_text[:28] + "..."
        c.drawCentredString(cx, top - 2 * mm, comp_text)
        top -= 6 * mm

        # Participant name (bold, may need wrapping)
        c.setFont(_FONT_BOLD, 8)
        name = badge.name
        if len(name) > 28:
            # Two-line name
            mid = name.rfind(" ", 0, 28)
            if mid == -1:
                mid = 28
            c.drawCentredString(cx, top - 2 * mm, name[:mid])
            c.drawCentredString(cx, top - 5 * mm - 2 * mm, name[mid:].strip())
            top -= 11 * mm
        else:
            c.drawCentredString(cx, top - 2 * mm, name)
            top -= 6 * mm

        # School (smaller)
        c.setFont(_FONT_REGULAR, 6)
        school = badge.school
        if len(school) > 35:
            school = school[:33] + "..."
        c.drawCentredString(cx, top - 2 * mm, school)
        top -= 6 * mm

        # QR code (centered)
        qr_bytes = self.qr_service.generate_qr_code(
            badge.qr_token, error_correction="H", box_size=6, border=1
        )
        qr_buffer = BytesIO(qr_bytes)
        qr_image = ImageReader(qr_buffer)
        qr_x = cx - self.QR_SIZE / 2
        qr_y = top - self.QR_SIZE - 1 * mm
        c.drawImage(
            qr_image, qr_x, qr_y, width=self.QR_SIZE, height=self.QR_SIZE,
            preserveAspectRatio=True,
        )

        # Hint text below QR
        c.setFont(_FONT_REGULAR, 5)
        c.setFillColor(colors.grey)
        c.drawCentredString(cx, qr_y - 3 * mm, "Покажите QR-код для допуска")
        c.setFillColor(colors.black)
