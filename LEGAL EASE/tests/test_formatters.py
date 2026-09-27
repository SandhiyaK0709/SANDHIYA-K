from document_utils.formatters import (
    sanitize_text,
    format_txt,
    format_docx,
    format_pdf,
)


def test_sanitize_text():
    text = "Hello   world\n\n\nTest"

    result = sanitize_text(text)

    assert "Hello" in result
    assert "world" in result


def test_format_txt():
    result = format_txt(
        title="Employment Contract",
        content="This is a sample employment contract.",
        document_type="Employment Contract",
        terms="Salary: INR 50,000",
    )

    assert isinstance(result, bytes)
    assert b"Employment Contract" in result


def test_format_docx():
    result = format_docx(
        title="Employment Contract",
        content="This is a sample employment contract.",
        document_type="Employment Contract",
        terms="Salary: INR 50,000",
    )

    assert isinstance(result, bytes)

    # DOCX files are ZIP files internally.
    assert result[:2] == b"PK"


def test_format_pdf():
    result = format_pdf(
        title="Employment Contract",
        content="This is a sample employment contract.",
        document_type="Employment Contract",
        terms="Salary: INR 50,000",
    )

    assert isinstance(result, bytes)

    # PDF files normally start with %PDF
    assert result[:4] == b"%PDF"