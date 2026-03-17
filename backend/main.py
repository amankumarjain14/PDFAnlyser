from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.pdf import router as pdf_router

app = FastAPI(
    title="PDF Analysis & Enhancement API",
    description="Upload a PDF, analyze with AI, and get an enhanced Word document.",
    version="1.0.0",
)

# CORS – allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "PDF Analysis & Enhancement API"})
