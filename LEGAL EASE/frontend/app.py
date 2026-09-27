import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "LegalEase")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚖️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #555;
        margin-bottom: 25px;
    }

    .legal-notice {
        padding: 15px;
        border-radius: 8px;
        background-color: #f3f4f6;
        border: 1px solid #d1d5db;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        color: #777;
        margin-top: 40px;
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=100)

st.markdown(
    f'<div class="main-title">⚖️ {APP_NAME}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-powered legal document drafting assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="legal-notice">
    <b>Important:</b> LegalEase generates documents using AI assistance.
    These documents are for informational and drafting purposes only and
    should be reviewed by a qualified legal professional before use.
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------

if "document" not in st.session_state:
    st.session_state.document = None

if "document_title" not in st.session_state:
    st.session_state.document_title = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("📄 Document Details")

document_type = st.sidebar.selectbox(
    "Document Type",
    [
        "Employment Contract",
        "Lease Agreement",
        "Non-Disclosure Agreement (NDA)",
        "Freelance Contract",
        "Offer Letter",
        "General Agreement",
        "Custom",
    ],
)

parties = st.sidebar.text_area(
    "Parties",
    placeholder=(
        "Example:\n"
        "Employer: ABC Technologies Pvt Ltd\n"
        "Employee: Priya Kumar"
    ),
    height=130,
)

terms = st.sidebar.text_area(
    "Terms & Conditions",
    placeholder=(
        "Example:\n"
        "Salary: ₹50,000 per month\n"
        "Work location: Chennai\n"
        "Notice period: 30 days"
    ),
    height=180,
)

dates = st.sidebar.text_area(
    "Important Dates",
    placeholder=(
        "Example:\n"
        "Start Date: 01/10/2026\n"
        "End Date: 30/09/2027"
    ),
    height=100,
)


# -----------------------------
# Generate button
# -----------------------------

generate_button = st.sidebar.button(
    "✨ Generate Document",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():
        st.sidebar.error("Please enter the parties.")

    elif not terms.strip():
        st.sidebar.error("Please enter the terms and conditions.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }

        try:

            with st.spinner("Generating your legal document..."):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

            if response.status_code == 200:

                data = response.json()

                st.session_state.document = data["content"]
                st.session_state.document_title = data["title"]
                st.session_state.document_type = data["document_type"]

                st.success("Document generated successfully! 🎉")

            else:

                try:
                    error_detail = response.json().get(
                        "detail",
                        response.text,
                    )
                except Exception:
                    error_detail = response.text

                st.error(
                    f"Backend error ({response.status_code}): "
                    f"{error_detail}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Backend server is not running.\n\n"
                "Please start FastAPI first using:\n"
                "`uvicorn backend.main:app --reload`"
            )

        except Exception as exc:

            st.error(f"Something went wrong: {exc}")


# -----------------------------
# Document Preview
# -----------------------------

if st.session_state.document:

    st.divider()

    st.subheader("📑 Generated Document")

    tab1, tab2 = st.tabs(
        [
            "👁️ Preview",
            "✏️ Edit",
        ]
    )

    with tab1:

        st.markdown(
            f"### {st.session_state.document_title}"
        )

        st.text_area(
            "Document Preview",
            value=st.session_state.document,
            height=600,
            disabled=True,
        )

    with tab2:

        edited_document = st.text_area(
            "Edit your document",
            value=st.session_state.document,
            height=600,
        )

        if st.button("💾 Save Edits"):

            st.session_state.document = edited_document

            st.success("Changes saved successfully.")


    # -----------------------------
    # Download section
    # -----------------------------

    st.divider()

    st.subheader("⬇️ Download Document")

    download_col1, download_col2, download_col3 = st.columns(3)


    export_payload = {
        "document_type": st.session_state.document_type,
        "title": st.session_state.document_title,
        "content": st.session_state.document,
        "terms": terms,
    }


    # TXT
    with download_col1:

        try:

            txt_response = requests.post(
                f"{BACKEND_URL}/export/txt",
                json=export_payload,
                timeout=60,
            )

            if txt_response.status_code == 200:

                st.download_button(
                    label="📄 Download TXT",
                    data=txt_response.content,
                    file_name="legalease_document.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        except Exception:
            st.warning("TXT export unavailable.")


    # DOCX
    with download_col2:

        try:

            docx_response = requests.post(
                f"{BACKEND_URL}/export/docx",
                json=export_payload,
                timeout=60,
            )

            if docx_response.status_code == 200:

                st.download_button(
                    label="📝 Download DOCX",
                    data=docx_response.content,
                    file_name="legalease_document.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    use_container_width=True,
                )

        except Exception:
            st.warning("DOCX export unavailable.")


    # PDF
    with download_col3:

        try:

            pdf_response = requests.post(
                f"{BACKEND_URL}/export/pdf",
                json=export_payload,
                timeout=60,
            )

            if pdf_response.status_code == 200:

                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_response.content,
                    file_name="legalease_document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        except Exception:
            st.warning("PDF export unavailable.")


# -----------------------------
# Footer
# -----------------------------

st.markdown(
    """
    <div class="footer">
        LegalEase — AI-assisted legal document drafting<br>
        Please consult a qualified legal professional before using
        any generated document.
    </div>
    """,
    unsafe_allow_html=True,
)