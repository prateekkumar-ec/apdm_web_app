import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# Mock data
pdf_file_doc = {"file_id": "123", "file_type": "pdf", "stored_path": "/fake/path.pdf"}
audio_file_doc = {"file_id": "456", "file_type": "audio", "stored_path": "/fake/path.mp3"}
unsupported_file_doc = {"file_id": "789", "file_type": "txt", "stored_path": "/fake/path.txt"}

# 1️⃣ File not found
@patch("app.db.mongo.files_collection.find_one")
def test_file_not_found(mock_find):
    mock_find.return_value = None
    response = client.post("/process/000")
    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}

# 2️⃣ PDF file
@patch("app.api.process.extract_text_from_pdf")
@patch("app.db.mongo.update_file_text")
@patch("app.db.mongo.files_collection.find_one")
def test_pdf_file(mock_find, mock_update, mock_extract):
    mock_find.return_value = pdf_file_doc
    mock_extract.return_value = "Extracted PDF text"
    
    response = client.post("/process/123")
    
    assert response.status_code == 200
    assert response.json() == {"file_id": "123", "message": "Processing complete"}
    mock_extract.assert_called_once_with("/fake/path.pdf")
    mock_update.assert_called_once_with("123", "Extracted PDF text")

# 3️⃣ Audio/Video file
@patch("app.api.process.transcribe_audio")
@patch("app.db.mongo.update_file_text")
@patch("app.db.mongo.files_collection.find_one")
def test_audio_file(mock_find, mock_update, mock_transcribe):
    mock_find.return_value = audio_file_doc
    mock_transcribe.return_value = "Transcribed audio text"
    
    response = client.post("/process/456")
    
    assert response.status_code == 200
    assert response.json() == {"file_id": "456", "message": "Processing complete"}
    mock_transcribe.assert_called_once_with("/fake/path.mp3")
    mock_update.assert_called_once_with("456", "Transcribed audio text")

# 4️⃣ Unsupported file type
@patch("app.db.mongo.files_collection.find_one")
def test_unsupported_file_type(mock_find):
    mock_find.return_value = unsupported_file_doc
    response = client.post("/process/789")
    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported file type"}
