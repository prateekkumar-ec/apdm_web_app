# tests/test_vector_store.py
import os
import pytest
from unittest.mock import patch, MagicMock

import app.db.vector_store as vs

def test_save_vectorstore_creates_folder_and_calls_save():
    mock_vectorstore = MagicMock()
    file_id = "test/file"

    with patch("os.makedirs") as mock_makedirs:
        vs.save_vectorstore(mock_vectorstore, file_id)

        safe_file_id = file_id.replace("/", "_")
        folder_path = os.path.join(vs.VECTORSTORE_DIR, safe_file_id)

        mock_makedirs.assert_called_once_with(folder_path, exist_ok=True)
        mock_vectorstore.save_local.assert_called_once_with(folder_path)

@patch("os.path.exists")
@patch("os.listdir")
@patch("app.db.vector_store.FAISS.load_local")
def test_load_vectorstore_folder_not_exists(mock_load, mock_listdir, mock_exists):
    file_id = "nonexistent"
    # Folder does not exist
    mock_exists.return_value = False

    result = vs.load_vectorstore(file_id)
    assert result is None
    mock_load.assert_not_called()

@patch("os.path.exists")
@patch("os.listdir")
@patch("app.db.vector_store.FAISS.load_local")
def test_load_vectorstore_folder_empty(mock_load, mock_listdir, mock_exists):
    file_id = "emptyfolder"
    mock_exists.return_value = True
    mock_listdir.return_value = []  # empty folder

    result = vs.load_vectorstore(file_id)
    assert result is None
    mock_load.assert_not_called()

@patch("os.path.exists")
@patch("os.listdir")
@patch("app.db.vector_store.FAISS.load_local")
def test_load_vectorstore_loads_successfully(mock_load, mock_listdir, mock_exists):
    file_id = "existing"
    mock_exists.return_value = True
    mock_listdir.return_value = ["file1", "file2"]

    mock_vectorstore = MagicMock()
    mock_load.return_value = mock_vectorstore

    result = vs.load_vectorstore(file_id)

    safe_file_id = file_id.replace("/", "_")
    folder_path = os.path.join(vs.VECTORSTORE_DIR, safe_file_id)

    mock_load.assert_called_once_with(folder_path, vs.embeddings, allow_dangerous_deserialization=True)
    assert result == mock_vectorstore
