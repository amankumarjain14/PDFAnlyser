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
    
    if file_type == "pdf":
        if not os.path.exists(settings.UPLOAD_DIR):
            raise HTTPException(status_code=404, detail="Upload directory missing.")
        for f in os.listdir(settings.UPLOAD_DIR):
            if f.startswith(f"{job_id}_"):
                return FileResponse(os.path.join(settings.UPLOAD_DIR, f), filename=f[len(job_id)+1:])
    elif file_type == "docx":
        path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_enhanced.docx")
        if os.path.exists(path):
            return FileResponse(path, filename=f"enhanced_{job_id}.docx")
            
    raise HTTPException(status_code=404, detail="File not found.")
