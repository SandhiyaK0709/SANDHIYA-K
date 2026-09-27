import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiGenerationError(Exception):
    """Raised when document generation fails."""


@dataclass
class GeneratedDocument:
    title: str
    content: str
    generated_by: str


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant for drafting legal documents.

Create clear, professional legal document drafts based ONLY on the
information supplied by the user.

Important rules:
- Do not invent names, addresses, dates, amounts, or other facts.
- If an important fact is missing, use a clear placeholder such as
  [INSERT DATE] or [INSERT AMOUNT].
- Use professional legal language.
- Organize the document with a title and clear sections.
- Include the supplied terms accurately.
- End with a short notice that the document is an AI-generated draft
  and should be reviewed by a qualified legal professional.
"""


def _mock_document(
    document_type: str,
    parties: str,
    terms: str,
    dates: str,
) -> GeneratedDocument:

    title = f"{document_type.title()}"

    content = f"""{title}

PARTIES
{parties}

DATES
{dates or "[INSERT DATE]"}

AGREEMENT

This document is a draft {document_type.lower()} prepared from the
information supplied by the user.

KEY TERMS

{terms}

GENERAL PROVISIONS

The parties intend to be bound by the terms described in this draft,
subject to review, completion of any missing information, and execution
by the appropriate parties.

LEGAL NOTICE

This document was generated using AI assistance for informational
purposes. It is a draft and should be reviewed by a qualified legal
professional before use.
"""

    return GeneratedDocument(
        title=title,
        content=content,
        generated_by="mock",
    )


class GeminiDocumentGenerator:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.mock_ai = (
            os.getenv("MOCK_AI", "false").lower() == "true"
        )

        self.temperature = float(
            os.getenv("AI_TEMPERATURE", "0.2")
        )

        self.max_output_tokens = int(
            os.getenv("AI_MAX_OUTPUT_TOKENS", "6000")
        )

        self.client = None

        if not self.mock_ai:
            if not self.api_key:
                raise GeminiGenerationError(
                    "GEMINI_API_KEY is missing. "
                    "Set it in the .env file or use MOCK_AI=true."
                )

            self.client = genai.Client(
                api_key=self.api_key
            )

    def generate(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str = "",
    ) -> GeneratedDocument:

        if self.mock_ai:
            return _mock_document(
                document_type=document_type,
                parties=parties,
                terms=terms,
                dates=dates,
            )

        prompt = f"""
Create a legal document draft.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

DATES:
{dates}

TERMS:
{terms}

Return ONLY the complete legal document text.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                ),
            )

            content = (response.text or "").strip()

            if not content:
                raise GeminiGenerationError(
                    "Gemini returned an empty response."
                )

            return GeneratedDocument(
                title=document_type.title(),
                content=content,
                generated_by="gemini",
            )

        except Exception as exc:
            raise GeminiGenerationError(
                f"Gemini generation failed: {exc}"
            ) from exc