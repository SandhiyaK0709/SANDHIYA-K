import os

os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_document():
    payload = {
        "document_type": "Employment Contract",
        "parties": "Employer: ABC Technologies\nEmployee: John Doe",
        "terms": "Monthly salary: INR 50,000. Working hours: 9 AM to 6 PM.",
        "dates": "Start date: 01-10-2026"
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "content" in data
    assert data["document_type"] == "Employment Contract"


def test_generate_validation():
    payload = {
        "document_type": "",
        "parties": "",
        "terms": ""
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 422