from fastapi import APIRouter, HTTPException
from app.db.mongo import files_collection, update_file_text
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.transcriber import transcribe_audio

router = APIRouter(prefix="/process", tags=["Process"])

@router.post("/{file_id}")
async def process_file(file_id: str):
    file_doc = files_collection.find_one({"file_id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    file_type = file_doc["file_type"]
    path = file_doc["stored_path"]

    if file_type == "pdf":
        text = extract_text_from_pdf(path)
    elif file_type in ("audio", "video"):
        text = transcribe_audio(path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    update_file_text(file_id, text)
    return {"file_id": file_id, "message": "Processing complete"}
