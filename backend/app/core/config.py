import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "aidm_db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "vectorstore")