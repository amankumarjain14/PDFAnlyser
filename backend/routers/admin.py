from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from typing import Optional
import os
from models.schemas import AdminStats
from services.tracking import get_stats
from config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password")):
    if x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password.")
    
    stats = get_stats()
    if not stats:
        raise HTTPException(status_code=500, detail="Could not retrieve statistics.")
    return stats

@router.get("/download/{file_type}/{job_id}")
async def admin_download(file_type: str, job_id: str, x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password")):
    if x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password.")
    
    # Ensure directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    if file_type == "pdf":
        print(f"DEBUG: Admin PDF download for {job_id} in {settings.UPLOAD_DIR}")
        for f in os.listdir(settings.UPLOAD_DIR):
            if f.startswith(f"{job_id}_"):
                file_path = os.path.join(settings.UPLOAD_DIR, f)
                return FileResponse(file_path, filename=f[len(job_id)+1:])
        print(f"DEBUG: PDF {job_id} not found in {os.listdir(settings.UPLOAD_DIR)}")
    elif file_type == "docx":
        print(f"DEBUG: Admin DOCX download search for {job_id} in {settings.OUTPUT_DIR}")
        if not os.path.exists(settings.OUTPUT_DIR):
            raise HTTPException(status_code=404, detail="Output directory missing.")
        for f in os.listdir(settings.OUTPUT_DIR):
            if f.startswith(f"{job_id}_"):
                file_path = os.path.join(settings.OUTPUT_DIR, f)
                return FileResponse(file_path, filename=f[len(job_id)+1:])
        print(f"DEBUG: DOCX {job_id} not found in {os.listdir(settings.OUTPUT_DIR)}")
            
    raise HTTPException(status_code=404, detail=f"File not found for job {job_id}. Note: Files are deleted on server restart.")
