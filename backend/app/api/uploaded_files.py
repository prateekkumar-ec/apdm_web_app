from fastapi import APIRouter
from app.db.mongo import files_collection

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("")
def get_uploaded_files():
    """Get list of all uploaded files"""
    files = list(files_collection.find(
        {},
        {"_id": 0, "file_id": 1, "original_name": 1, "file_type": 1, "uploaded_at": 1, "status": 1}
    ).sort("uploaded_at", -1).limit(50))
    
    return {"files": files}

@router.get("/{file_id}")
def get_file_details(file_id: str):
    """Get details of a specific file"""
    file_doc = files_collection.find_one(
        {"file_id": file_id},
        {"_id": 0}
    )
    
    if not file_doc:
        return {"error": "File not found"}
    
    return file_doc
