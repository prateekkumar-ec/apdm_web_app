import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# Mock data
mock_files_list = [
    {"file_id": "1", "original_name": "doc1.pdf", "file_type": "pdf", "uploaded_at": "2026-01-29", "status": "processed"},
    {"file_id": "2", "original_name": "audio1.mp3", "file_type": "audio", "uploaded_at": "2026-01-28", "status": "pending"}
]

mock_file_detail = {
    "file_id": "1",
    "original_name": "doc1.pdf",
    "file_type": "pdf",
    "uploaded_at": "2026-01-29",
    "status": "processed",
    "stored_path": "/tmp/doc1.pdf",
    "extracted_text": "Hello world"
}

# 1️⃣ Test GET /files
@patch("app.api.uploaded_files.files_collection.find")
def test_get_uploaded_files(mock_find):
    # Mock the chained calls: find().sort().limit()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value.limit.return_value = mock_files_list
    mock_find.return_value = mock_cursor

    response = client.get("/files")
    assert response.status_code == 200
    assert response.json() == {"files": mock_files_list}

# 2️⃣ Test GET /files/{file_id} when file exists
@patch("app.api.uploaded_files.files_collection.find_one")
def test_get_file_details_exists(mock_find_one):
    mock_find_one.return_value = mock_file_detail

    response = client.get("/files/1")
    assert response.status_code == 200
    assert response.json() == mock_file_detail
    mock_find_one.assert_called_once_with({"file_id": "1"}, {"_id": 0})

# 3️⃣ Test GET /files/{file_id} when file does NOT exist
@patch("app.api.uploaded_files.files_collection.find_one")
def test_get_file_details_not_exists(mock_find_one):
    mock_find_one.return_value = None

    response = client.get("/files/999")
    assert response.status_code == 200
    assert response.json() == {"error": "File not found"}
    mock_find_one.assert_called_once_with({"file_id": "999"}, {"_id": 0})
