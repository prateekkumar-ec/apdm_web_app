import pytest
import mongomock
from unittest.mock import patch
from app.db.mongo import update_file_text

# Use mongomock to create a fake MongoDB client for testing
@pytest.fixture
def mock_db():
    # We patch the files_collection in your mongo.py file
    with patch("app.db.mongo.files_collection", mongomock.MongoClient().db.files) as mocked:
        yield mocked

def test_update_file_text_pdf(mock_db):
    # 1. Insert a dummy record first
    file_id = "test_pdf_1"
    mock_db.insert_one({"file_id": file_id, "status": "pending"})

    # 2. Run the update
    update_file_text(file_id, "Extracted PDF content")

    # 3. Verify
    updated_doc = mock_db.find_one({"file_id": file_id})
    assert updated_doc["status"] == "processed"
    assert updated_doc["extracted_text"] == "Extracted PDF content"
    assert "segments" not in updated_doc # Should be missing for PDF

def test_update_file_text_audio(mock_db):
    # 1. Setup
    file_id = "test_audio_1"
    mock_db.insert_one({"file_id": file_id, "status": "pending"})
    fake_segments = [{"start": 0, "end": 5, "text": "Hello"}]

    # 2. Run
    update_file_text(file_id, "Transcript text", segments=fake_segments)

    # 3. Verify
    updated_doc = mock_db.find_one({"file_id": file_id})
    assert updated_doc["status"] == "processed"
    assert updated_doc["segments"] == fake_segments
    assert len(updated_doc["segments"]) == 1

def test_update_non_existent_file(mock_db):
    # Running update on a missing file should not crash
    # MongoDB update_one just does nothing if the filter doesn't match
    try:
        update_file_text("ghost_id", "some text")
    except Exception as e:
        pytest.fail(f"update_file_text raised {e} unexpectedly!")
