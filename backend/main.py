from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from routers.pdf import router as pdf_router
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
