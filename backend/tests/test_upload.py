# tests/test_upload.py
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ---------------------------
# 1️⃣ Successful PDF upload
# ---------------------------
@patch("app.api.upload.files_collection.insert_one")
def test_upload_pdf(mock_insert):
    # Create a fake PDF file
    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["file_name"] == "test.pdf"
    assert data["extension"] == "pdf"
    assert data["message"] == "File uploaded successfully"

    # Ensure insert_one was called
    assert mock_insert.called
    inserted_doc = mock_insert.call_args[0][0]
    assert inserted_doc["original_name"] == "test.pdf"
    assert inserted_doc["file_type"] == "pdf"
    assert inserted_doc["status"] == "uploaded"


# ---------------------------
# 2️⃣ Unsupported file type
# ---------------------------
def test_upload_unsupported_type():
    file_content = b"some content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported file type"}


# ---------------------------
# 3️⃣ Test audio upload
# ---------------------------
@patch("app.api.upload.files_collection.insert_one")
def test_upload_audio(mock_insert):
    file_content = b"fake audio content"
    files = {"file": ("song.mp3", io.BytesIO(file_content), "audio/mpeg")}

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["extension"] == "mp3"
    assert data["file_name"] == "song.mp3"
    assert data["message"] == "File uploaded successfully"
    assert mock_insert.called
    inserted_doc = mock_insert.call_args[0][0]
    assert inserted_doc["file_type"] == "audio"
