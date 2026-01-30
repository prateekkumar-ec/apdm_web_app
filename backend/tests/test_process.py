import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app  # Import your FastAPI app instance

client = TestClient(app)

# Test cases for different file types
@pytest.mark.parametrize("file_type", ["pdf", "audio"])
@patch("app.api.process.files_collection")
@patch("app.api.process.extract_text_from_pdf")
@patch("app.api.process.transcribe_audio")
@patch("app.api.process.update_file_text")
def test_process_file_success(
    mock_update, mock_transcribe, mock_extract, mock_mongo, file_type
):
    # 1. Setup Mock Data
    file_id = "test_file_id"
    mock_mongo.find_one.return_value = {
        "file_id": file_id,
        "file_type": file_type,
        "stored_path": f"/tmp/test.{file_type}"
    }

    # Setup specific mock returns for each service
    mock_extract.return_value = "Extracted PDF text"
    mock_transcribe.return_value = {
        "text": "Transcribed audio text",
        "segments": [{"start": 0.0, "end": 5.0, "text": "Hello"}]
    }

    # 2. Execute Request
    response = client.post(f"/process/{file_id}")

    # 3. Assertions
    assert response.status_code == 200
    assert response.json() == {"file_id": file_id, "message": "Processing complete"}
    
    # Verify the database was updated
    mock_update.assert_called_once()
    
    # Verify the correct service was called
    if file_type == "pdf":
        mock_extract.assert_called_once_with(f"/tmp/test.{file_type}")
    else:
        mock_transcribe.assert_called_once_with(f"/tmp/test.{file_type}")

@patch("app.api.process.files_collection")
def test_process_file_not_found(mock_mongo):
    # Mock MongoDB returning None
    mock_mongo.find_one.return_value = None
    
    response = client.post("/process/invalid_id")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

@patch("app.api.process.files_collection")
def test_unsupported_file_type(mock_mongo):
    mock_mongo.find_one.return_value = {
        "file_id": "bad_file",
        "file_type": "exe",
        "stored_path": "/tmp/test.exe"
    }
    
    response = client.post("/process/bad_file")
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"
