from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt
from fpdf import FPDF
from fpdf.enums import XPos, YPos


BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"


def sanitize_text(text: str) -> str:
    """Clean text before putting it into exported documents."""
    if not text:
        return ""

    replacements = {
        "\r\n": "\n",
        "\r": "\n",
        "\x00": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def format_txt(
    title: str,
    content: str,
    document_type: str = "",
    terms: str = "",
) -> bytes:
    """Create a plain TXT document."""
    title = sanitize_text(title)
    content = sanitize_text(content)
    terms = sanitize_text(terms)

    output = []

    output.append("LEGALEASE")
    output.append("=" * 70)
    output.append(title)
    output.append("=" * 70)

    if document_type:
        output.append(f"Document Type: {document_type}")

    output.append("")
    output.append(content)

    if terms:
        output.append("")
        output.append("KEY TERMS")
        output.append("-" * 70)
        output.append(terms)

    output.append("")
    output.append("Generated using LegalEase.")
    output.append("This document is provided for informational purposes and")
    output.append("should be reviewed by a qualified legal professional.")

    return "\n".join(output).encode("utf-8")


def _set_docx_font(document: Document) -> None:
    """Set the default document font to Times New Roman."""
    styles = document.styles

    for style_name in ["Normal", "Title", "Heading 1", "Heading 2", "Heading 3"]:
        try:
            style = styles[style_name]
            style.font.name = "Times New Roman"
            style.font.size = Pt(12)
        except KeyError:
            pass


def format_docx(
    title: str,
    content: str,
    document_type: str = "",
    terms: str = "",
) -> bytes:
    """Create a branded DOCX legal document."""
    title = sanitize_text(title)
    content = sanitize_text(content)
    terms = sanitize_text(terms)

    document = Document()

    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    _set_docx_font(document)

    # Logo
    if LOGO_PATH.exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = paragraph.add_run()
        run.add_picture(str(LOGO_PATH), width=Inches(1.25))

    # Brand
    brand = document.add_paragraph()
    brand.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = brand.add_run("LEGALEASE")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    # Title
    title_paragraph = document.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = title_paragraph.add_run(title)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(18)

    # Document type
    if document_type:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = paragraph.add_run(document_type)
        run.italic = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)

    document.add_paragraph()

    # Main content
    for block in content.split("\n"):
        block = block.strip()

        if not block:
            document.add_paragraph()
            continue

        upper = block.upper()

        # Simple heading detection
        if (
            len(block) < 100
            and (
                upper.startswith("ARTICLE ")
                or upper.startswith("SECTION ")
                or upper.startswith("1.")
                or upper.startswith("2.")
                or upper.startswith("3.")
                or upper.startswith("4.")
                or upper.startswith("5.")
                or upper.startswith("6.")
                or upper.startswith("7.")
                or upper.startswith("8.")
                or upper.startswith("9.")
            )
        ):
            paragraph = document.add_paragraph()
            run = paragraph.add_run(block)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
        else:
            paragraph = document.add_paragraph(block)
            paragraph.paragraph_format.space_after = Pt(6)

            for run in paragraph.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)

    # Key terms table
    if terms:
        document.add_paragraph()

        heading = document.add_paragraph()
        run = heading.add_run("KEY TERMS")
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)

        table = document.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        header_cells = table.rows[0].cells
        header_cells[0].text = "Term"
        header_cells[1].text = "Details"

        for line in terms.splitlines():
            line = line.strip()

            if not line:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
            elif "-" in line:
                key, value = line.split("-", 1)
            else:
                key, value = "Term", line

            cells = table.add_row().cells
            cells[0].text = key.strip()
            cells[1].text = value.strip()

    # Footer
    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    footer_run = footer_paragraph.add_run(
        "LegalEase | AI-assisted legal document drafting | "
        "Review with a qualified legal professional"
    )
    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(9)

    # Save to memory
    buffer = BytesIO()
    document.save(buffer)

    return buffer.getvalue()


class LegalPDF(FPDF):
    """Custom PDF class for LegalEase branding."""

    def header(self):
        if LOGO_PATH.exists():
            try:
                self.image(str(LOGO_PATH), x=10, y=8, w=25)
            except Exception:
                pass

        self.set_font("Times", "B", 14)
        self.cell(
            0,
            10,
            "LEGALEASE",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

        self.ln(3)

    def footer(self):
        self.set_y(-15)

        self.set_font("Times", "", 8)
        self.cell(
            0,
            5,
            f"LegalEase | Page {self.page_no()}",
            align="C",
        )


def format_pdf(
    title: str,
    content: str,
    document_type: str = "",
    terms: str = "",
) -> bytes:
    """Create a branded PDF legal document."""
    title = sanitize_text(title)
    content = sanitize_text(content)
    terms = sanitize_text(terms)

    pdf = LegalPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Times", "B", 18)
    pdf.multi_cell(0, 10, title, align="C")
    pdf.ln(2)

    # Document type
    if document_type:
        pdf.set_font("Times", "I", 11)
        pdf.multi_cell(0, 7, document_type, align="C")
        pdf.ln(5)

    # Main content
    for block in content.split("\n"):
        block = block.strip()

        if not block:
            pdf.ln(4)
            continue

        upper = block.upper()

        if (
            len(block) < 100
            and (
                upper.startswith("ARTICLE ")
                or upper.startswith("SECTION ")
                or upper.startswith("1.")
                or upper.startswith("2.")
                or upper.startswith("3.")
                or upper.startswith("4.")
                or upper.startswith("5.")
                or upper.startswith("6.")
                or upper.startswith("7.")
                or upper.startswith("8.")
                or upper.startswith("9.")
            )
        ):
            pdf.set_font("Times", "B", 13)
            pdf.multi_cell(0, 7, block)
            pdf.ln(2)
        else:
            pdf.set_font("Times", "", 11)
            pdf.multi_cell(0, 6, block)
            pdf.ln(2)

    # Key terms
    if terms:
        pdf.ln(3)

        pdf.set_font("Times", "B", 13)
        pdf.cell(
            0,
            7,
            "KEY TERMS",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

        pdf.set_font("Times", "", 11)

        for line in terms.splitlines():
            line = line.strip()

            if not line:
                continue

            pdf.multi_cell(0, 6, line)

    # Legal notice
    pdf.ln(5)
    pdf.set_font("Times", "I", 9)

    notice = (
        "LegalEase generated this document using AI assistance. "
        "This document is provided for informational purposes and "
        "should be reviewed by a qualified legal professional."
    )

    pdf.multi_cell(0, 5, notice)

    return bytes(pdf.output())