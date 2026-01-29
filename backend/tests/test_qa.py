import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api.qa import current_file_id, current_memory, get_memory_for_file

client = TestClient(app)

# Mock processed file
processed_file = {"file_id": "123", "extracted_text": "Hello world"}

# ---------------------------
# 1️⃣ File not processed
# ---------------------------
@patch("app.db.mongo.files_collection.find_one")
def test_file_not_processed(mock_find):
    mock_find.return_value = None
    response = client.post("/qa", json={"file_id": "999", "question": "What is this?"})
    assert response.status_code == 404
    assert response.json() == {"detail": "File not processed"}


# ---------------------------
# 2️⃣ Vectorstore exists
# ---------------------------
@patch("app.db.mongo.files_collection.find_one")
@patch("app.db.vector_store.load_vectorstore")
@patch("app.db.vector_store.save_vectorstore")
@patch("app.api.qa.ConversationalRetrievalChain.from_llm")
def test_vectorstore_exists(mock_chain, mock_save, mock_load, mock_find):
    mock_find.return_value = processed_file
    mock_vectorstore = MagicMock()
    mock_vectorstore.as_retriever.return_value = "retriever_mock"
    mock_load.return_value = mock_vectorstore

    mock_chain_instance = MagicMock()
    mock_chain_instance.run.return_value = "Fake answer"
    mock_chain.return_value = mock_chain_instance

    response = client.post("/qa", json={"file_id": "123", "question": "Hello?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Fake answer"}
    mock_load.assert_called_once_with(file_id="123")
    mock_chain.assert_called_once()


# ---------------------------
# 3️⃣ Vectorstore does NOT exist → create_docs + FAISS
# ---------------------------
@patch("app.db.mongo.files_collection.find_one")
@patch("app.db.vector_store.load_vectorstore")
@patch("app.db.vector_store.save_vectorstore")
@patch("app.services.document_processor.create_docs")
@patch("app.api.qa.FAISS.from_documents")
@patch("app.api.qa.ConversationalRetrievalChain.from_llm")
def test_vectorstore_not_exists(
    mock_chain, mock_faiss, mock_create_docs, mock_save, mock_load, mock_find
):
    # File is processed
    mock_find.return_value = processed_file
    mock_load.return_value = None  # vectorstore doesn't exist

    # Mock docs creation
    mock_docs = ["doc1", "doc2"]
    mock_create_docs.return_value = mock_docs

    # Mock FAISS
    mock_vectorstore = MagicMock()
    mock_vectorstore.as_retriever.return_value = "retriever_mock"
    mock_faiss.return_value = mock_vectorstore

    # Mock LLM chain
    mock_chain_instance = MagicMock()
    mock_chain_instance.run.return_value = "Answer from LLM"
    mock_chain.return_value = mock_chain_instance

    # Call endpoint
    response = client.post("/qa", json={"file_id": "123", "question": "Hello?"})

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"answer": "Answer from LLM"}
    mock_create_docs.assert_called_once_with("Hello world")
    mock_faiss.assert_called_once_with(mock_docs, patch("app.db.vector_store.embeddings"))
    mock_save.assert_called_once_with(mock_vectorstore, file_id="123")
    mock_chain.assert_called_once()


# ---------------------------
# 4️⃣ Test get_memory_for_file resets memory
# ---------------------------
def test_get_memory_for_file_resets():
    global current_file_id, current_memory
    current_file_id = "old"
    current_memory = MagicMock()

    mem1 = get_memory_for_file("new_file")
    assert mem1 is not current_memory  # new memory created
    mem2 = get_memory_for_file("new_file")
    assert mem2 is mem1  # same memory reused
