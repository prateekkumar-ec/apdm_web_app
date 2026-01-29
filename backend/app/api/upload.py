import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime

from app.core.config import UPLOAD_DIR
from app.db.mongo import files_collection

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "audio/mpeg": "audio",
    "audio/wav": "audio",
    "video/mp4": "video"
}

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    filename = f"{file_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_doc = {
        "file_id": file_id,
        "original_name": file.filename,
        "stored_path": file_path,
        "file_type": ALLOWED_TYPES[file.content_type],
        "content_type": file.content_type,
        "uploaded_at": datetime.utcnow(),
        "status": "uploaded"
    }

    files_collection.insert_one(file_doc)

    return {
        "file_id": file_id,
        "file_name": file.filename,
        "extension": extension,
        "message": "File uploaded successfully"
    }
