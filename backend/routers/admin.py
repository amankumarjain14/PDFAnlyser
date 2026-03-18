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
    job_id = job_id.strip()
    if x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password.")
    
    # Ensure directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    search_dir = settings.UPLOAD_DIR if file_type == "pdf" else settings.OUTPUT_DIR
    files_in_dir = os.listdir(search_dir) if os.path.exists(search_dir) else []
    
    print(f"DIAGNOSTIC: Admin {file_type} download for job_id: {job_id}")
    print(f"DIAGNOSTIC: Search directory: {search_dir}")
    print(f"DIAGNOSTIC: Current working directory: {os.getcwd()}")
    print(f"DIAGNOSTIC: Files found in dir: {files_in_dir}")

    for f in files_in_dir:
        if f.startswith(f"{job_id}_"):
            file_path = os.path.join(search_dir, f)
            return FileResponse(file_path, filename=f[len(job_id)+1:])
            
    # If not found, raise a very descriptive error
    dir_summary = f"{len(files_in_dir)} files in {search_dir}"
    raise HTTPException(
        status_code=404, 
        detail=f"File not found for job {job_id}. Type: {file_type}. "
               f"Search path: {search_dir}. Dir status: {dir_summary}. "
               f"Files: {files_in_dir[:5]}..."
    )
