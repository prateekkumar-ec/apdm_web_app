from pymongo import MongoClient
from app.core.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

files_collection = db["files"]


def update_file_text(file_id: str, text: str, segments: list = None):
    update_data = {"extracted_text": text, "status": "processed"}
    if segments is not None:
        update_data["segments"] = segments
    files_collection.update_one(
        {"file_id": file_id},
        {"$set": update_data}
    )
