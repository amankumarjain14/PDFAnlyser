from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from routers.pdf import router as pdf_router
from routers.admin import router as admin_router
from services.tracking import log_visit
import os

app = FastAPI(
    title="PDF Analysis & Enhancement API",
    description="Upload a PDF, analyze with AI, and get an enhanced Word document.",
    version="1.0.0",
)

# CORS – allow all origins for development/deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(admin_router)

# ── Visitor tracking middleware ──────────────────────────────────────────────
@app.middleware("http")
async def track_visits(request: Request, call_next):
    # Log visit if it's a page request or initial API hit
    if request.method == "GET" and not request.url.path.startswith("/api") and not request.url.path.startswith("/static"):
        ip = request.client.host if request.client else "unknown"
        ua = request.headers.get("user-agent", "unknown")
        log_visit(ip, ua)
    
    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "PDF Analysis & Enhancement API"})

# Serve static files from the 'static' directory
# This directory will exist in the Docker container after building the frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    # Catch-all route for SPA navigation
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"error": "Not Found"}, status_code=404)
