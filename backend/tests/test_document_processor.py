import pytest
from langchain_community.docstore.document import Document
from app.services.document_processor import create_docs

def test_create_docs_pdf_string():
    # Test with a long string (PDF case)
    long_text = "This is a test. " * 200  # Creates a long string > 1000 chars
    docs = create_docs(long_text)
    
    assert isinstance(docs, list)
    assert len(docs) > 1
    assert isinstance(docs[0], Document)
    # Check that chunks are roughly the right size
    assert len(docs[0].page_content) <= 1000

def test_create_docs_audio_segments():
    # 1. Create dummy segments (15 segments)
    fake_segments = [
        {"start": i * 5, "end": (i + 1) * 5, "text": f"Sentence {i}."}
        for i in range(15)
    ]
    
    # 2. Process segments
    docs = create_docs(fake_segments)
    
    # 3. Assertions for Sliding Window (Window=10, Step=5)
    # Total 15 segments:
    # Doc 1: Segs 0-9
    # Doc 2: Segs 5-14
    assert len(docs) == 2
    
    # Check Metadata for Doc 1
    assert docs[0].metadata["start"] == 0
    assert docs[0].metadata["end"] == 50 # 10th segment ends at 50
    assert len(docs[0].metadata["original_segments"]) == 10
    
    # Check Metadata for Doc 2 (Sliding overlap)
    assert docs[1].metadata["start"] == 25 # 6th segment starts at 25
    assert docs[1].metadata["end"] == 75 # 15th segment ends at 75
    
    # Check Content
    assert "Sentence 0." in docs[0].page_content
    assert "Sentence 14." in docs[1].page_content

def test_create_docs_empty_list():
    # Should return empty list for empty content
    assert create_docs([]) == []

def test_create_docs_invalid_format():
    # Should raise error for numbers/dicts
    with pytest.raises(ValueError, match="Unsupported extracted content format"):
        create_docs(12345)
