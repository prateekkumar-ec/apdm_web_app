import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.health import router as health_router
from app.core.config import UPLOAD_DIR
from app.api.upload import router as upload_router
from app.api.process import router as process_router
from app.api.qa import router as qa_router
from app.api.uploaded_files import router as files_router

app = FastAPI(
    title="AI Document & Multimedia Q&A",
    version="0.1.0"
)

# CORS settings for frontend on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount uploads directory for serving media files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(qa_router)
app.include_router(files_router)

@app.get("/")
def root():
    return {"message": "API is running"}
