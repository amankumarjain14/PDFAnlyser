from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models.schemas import AdminStats
from services.tracking import get_stats
from config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password")):
    # Debug print for local troubleshooting
    print(f"DEBUG: Admin login attempt with password: {x_admin_password}")
    
    if x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password.")
    
    stats = get_stats()
    if not stats:
        raise HTTPException(status_code=500, detail="Could not retrieve statistics.")
    
    return stats
