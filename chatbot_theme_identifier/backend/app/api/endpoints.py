from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from app.config import settings
from app.services.ocr import process_document

router = APIRouter()

@router.post("/upload", status_code=202)
async def upload_file(file: UploadFile = File(...)):
    if not any(file.filename.endswith(ext) for ext in settings.ALLOWED_TYPES):
        raise HTTPException(400, "Unsupported file format")
    
    save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            os.remove(save_path)
            raise HTTPException(413, "File too large")
        f.write(content)
    
    process_document.delay(save_path)
    return {"message": "File queued for processing"}

@router.post("/batch-upload", status_code=202)
async def batch_upload(files: List[UploadFile] = File(...)):
    if len(files) > 100:
        raise HTTPException(400, "Max 100 files per batch")
    
    saved_paths = []
    for file in files:
        if not any(file.filename.endswith(ext) for ext in settings.ALLOWED_TYPES):
            continue
        
        save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_paths.append(save_path)
    
    for path in saved_paths:
        process_document.delay(path)
    
    return {"message": f"{len(saved_paths)} files queued"}
