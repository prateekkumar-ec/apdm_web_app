# tests/test_document_processor.py
import pytest
from app.services.document_processor import create_docs
from langchain_community.docstore.document import Document

def test_create_docs_splits_text_correctly():
    text = "a" * 2500  # 2500 characters

    docs = create_docs(text)

    # Check type
    assert isinstance(docs, list)
    assert all(isinstance(doc, Document) for doc in docs)

    # Check chunk sizes (except last one may be smaller)
    for doc in docs[:-1]:
        assert len(doc.page_content) <= 1000

    # Total text coverage (all chars appear at least once)
    concatenated = "".join(doc.page_content for doc in docs)
    for char in text[:10]:  # quick spot-check first 10 chars
        assert char in concatenated

def test_create_docs_empty_text():
    docs = create_docs("")
    assert docs == []
