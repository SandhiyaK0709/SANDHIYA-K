from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=100)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=10000)
    dates: str = Field(default="", max_length=2000)


class GenerateResponse(BaseModel):
    document_type: str
    title: str
    content: str
    generated_by: str


class ExportRequest(BaseModel):
    document_type: str
    title: str
    content: str
    terms: str = ""