import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np

# Replace 'app.main' with the actual path to your FastAPI instance
from app.main import app 

client = TestClient(app)

# Helper to generate a fake embedding vector
def get_fake_embedding(dim=1536):
    return np.random.rand(dim).tolist()

@patch("app.api.qa.files_collection") # Added this missing patch
@patch("app.api.qa.load_vectorstore")
@patch("app.api.qa.create_docs")
@patch("app.api.qa.FAISS.from_documents")
@patch("app.api.qa.ConversationalRetrievalChain.from_llm") # Added to prevent chain crash
@patch("app.api.qa.embeddings") # Added to mock embedding call
def test_answer_question_creates_vectorstore(mock_embeddings, mock_chain_init, mock_faiss, mock_create_docs, mock_load_vs, mock_mongo):
    # Setup
    mock_load_vs.return_value = None
    mock_mongo.find_one.return_value = {
        "file_id": "new_file", 
        "segments": [{"text": "test", "start": 0, "end": 1}]
    }
    mock_create_docs.return_value = []
    
    # Mock chain to return something empty
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = {"answer": "test", "source_documents": []}
    mock_chain_init.return_value = mock_chain
    mock_embeddings.embed_query.return_value = [0.1] * 1536

    # Trigger
    response = client.post("/qa", json={"file_id": "new_file", "question": "test"})
    
    assert response.status_code == 200
    mock_create_docs.assert_called_once()
    mock_faiss.assert_called_once()

def test_get_memory_for_file_caching():
    from app.api.qa import get_memory_for_file
    
    mem1 = get_memory_for_file("same_id")
    mem2 = get_memory_for_file("same_id")
    
    # This covers the 'if' condition by NOT entering it the second time
    assert mem1 is mem2 

def test_merge_timestamps_logic():
    from app.api.qa import merge_timestamps
    
    input_ts = [
        {"start": 0, "end": 5, "text": "First"},
        {"start": 6, "end": 10, "text": "Merge me"},
        {"start": 20, "end": 25, "text": "Separate"} # Does not merge
    ]
    
    merged = merge_timestamps(input_ts)
    
    # This covers the if (merge path) and else (new segment path)
    assert len(merged) == 2
    assert merged[0]["end"] == 10
    assert merged[1]["start"] == 20


@patch("app.api.qa.files_collection")
@patch("app.api.qa.load_vectorstore")
@patch("app.api.qa.embeddings")
@patch("app.api.qa.ConversationalRetrievalChain.from_llm")
def test_answer_question_success(mock_chain_init, mock_embeddings, mock_load_vs, mock_mongo):
    # 1. Mock MongoDB response
    mock_mongo.find_one.return_value = {
        "file_id": "test_file_123",
        "segments": [{"text": "Hello world", "start": 0, "end": 5}]
    }

    # 2. Mock Vectorstore and Chain
    mock_vs = MagicMock()
    mock_load_vs.return_value = mock_vs
    
    # Mock LLM result with source documents containing 'original_segments'
    fake_ans_embedding = get_fake_embedding()
    mock_embeddings.embed_query.return_value = fake_ans_embedding
    
    mock_doc = MagicMock()
    mock_doc.metadata = {
        "original_segments": [
            {
                "text": "Hrithik is at IIT Delhi",
                "start": 10.0,
                "end": 15.0,
                "embedding": fake_ans_embedding # Ensure 1.0 similarity for test
            }
        ]
    }
    
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = {
        "answer": "Hrithik is at IIT Delhi",
        "source_documents": [mock_doc]
    }
    mock_chain_init.return_value = mock_chain

    # 3. Execute request
    payload = {"file_id": "test_file_123", "question": "Who is Hrithik?"}
    response = client.post("/qa", json=payload)

    # 4. Assertions
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "timestamps" in data
    assert len(data["timestamps"]) > 0
    assert data["timestamps"][0]["start"] == 10.0

def test_answer_question_file_not_found():
    with patch("app.api.qa.files_collection") as mock_mongo:
        mock_mongo.find_one.return_value = None
        response = client.post("/qa", json={"file_id": "invalid", "question": "hi"})
        assert response.status_code == 404
        assert response.json()["detail"] == "File not found!"
