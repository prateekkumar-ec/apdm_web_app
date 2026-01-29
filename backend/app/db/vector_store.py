from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from app.core.config import VECTORSTORE_DIR
from app.core.config import OPENAI_API_KEY
import os
# OpenAI embeddings instance
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)  # OR read from env


def save_vectorstore(vectorstore: FAISS, file_id: str):
    safe_file_id = file_id.replace("/", "_")
    folder_path = os.path.join(VECTORSTORE_DIR, safe_file_id)

    os.makedirs(folder_path, exist_ok=True)
    vectorstore.save_local(folder_path)

def load_vectorstore(file_id: str):
    safe_file_id = file_id.replace("/", "_")
    folder_path = os.path.join(VECTORSTORE_DIR, safe_file_id)

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        return None

    return FAISS.load_local(
        folder_path,
        embeddings,
        allow_dangerous_deserialization=True
    )