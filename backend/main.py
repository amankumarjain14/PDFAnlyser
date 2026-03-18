from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.pdf import router as pdf_router

app = FastAPI(
    title="PDF Analysis & Enhancement API",
    description="Upload a PDF, analyze with AI, and get an enhanced Word document.",
    version="1.0.0",
)

# CORS – allow all origins for deployment
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
