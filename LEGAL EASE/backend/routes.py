from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response

from ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest, GenerateResponse, ExportRequest
from document_utils.formatters import format_txt, format_docx, format_pdf


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LegalEase API",
    }


@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: DocumentRequest):
    try:
        result = generator.generate(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return GenerateResponse(
            document_type=request.document_type,
            title=result.title,
            content=result.content,
            generated_by=result.generated_by,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/export/txt")
def export_txt(request: ExportRequest):
    content = format_txt(
        title=request.title,
        content=request.content,
        document_type=request.document_type,
    )

    return PlainTextResponse(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": 'attachment; filename="legalease_document.txt"'
        },
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):
    file_bytes = format_docx(
        title=request.title,
        content=request.content,
        document_type=request.document_type,
        terms=request.terms,
    )

    return Response(
        content=file_bytes,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": 'attachment; filename="legalease_document.docx"'
        },
    )


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):
    file_bytes = format_pdf(
        title=request.title,
        content=request.content,
        document_type=request.document_type,
        terms=request.terms,
    )

    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="legalease_document.pdf"'
        },
    )