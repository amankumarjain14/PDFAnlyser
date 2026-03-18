import asyncio
import copy
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from services.pdf_extractor import extract_text_from_pdf
from models.schemas import (
    AnalysisResult,
    JobStatus,
    PipelineStep,
    ProgressEvent,
    StepStatus,
    PIPELINE_STEPS,
    ChatRequest,
    ChatResponse
)
from services.ai_agent import analyze_pdf_content
from services.document_generator import generate_docx
from services.google_drive import upload_to_drive
from config import settings

router = APIRouter(prefix="/api", tags=["pdf"])

# ── In-memory job store ────────────────────────────────────────────────────────
jobs: Dict[str, dict] = {}


def _fresh_steps():
    return [copy.deepcopy(s) for s in PIPELINE_STEPS]


def _update_step(steps, step_id: str, status: StepStatus, message: str = None):
    for s in steps:
        if s.id == step_id:
            s.status = status
            if message:
                s.message = message
            break


# ── Upload endpoint ────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Size guard
    contents = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    job_id = str(uuid.uuid4())
    upload_path = Path(settings.UPLOAD_DIR) / f"{job_id}_{file.filename}"
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(upload_path, "wb") as out_file:
        await out_file.write(contents)

    steps = _fresh_steps()
    jobs[job_id] = {
        "status": JobStatus.QUEUED,
        "steps": steps,
        "original_filename": file.filename,
        "upload_path": str(upload_path),
        "result": None,
        "error": None,
        "queue": asyncio.Queue(),
    }

    # Kick off processing in the background
    asyncio.create_task(_process_job(job_id))

    return {"job_id": job_id, "filename": file.filename}


# ── SSE progress stream ────────────────────────────────────────────────────────
@router.get("/progress/{job_id}")
async def progress_stream(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")

    async def event_generator():
        job = jobs[job_id]
        q: asyncio.Queue = job["queue"]
        while True:
            try:
                event: ProgressEvent = await asyncio.wait_for(q.get(), timeout=60)
                yield {"data": event.model_dump_json()}
                if event.job_status in (JobStatus.DONE, JobStatus.ERROR):
                    break
            except asyncio.TimeoutError:
                # Send keep-alive
                yield {"data": '{"ping": true}'}

    return EventSourceResponse(event_generator())


# ── Result endpoint ────────────────────────────────────────────────────────────
@router.get("/result/{job_id}", response_model=AnalysisResult)
async def get_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    job = jobs[job_id]
    if job["status"] != JobStatus.DONE:
        raise HTTPException(status_code=202, detail="Job not yet complete.")
    return job["result"]


# ── Chat endpoint ──────────────────────────────────────────────────────────────
@router.post("/chat/{job_id}", response_model=ChatResponse)
async def chat_with_document(job_id: str, request: ChatRequest):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    job = jobs[job_id]
    if job["status"] != JobStatus.DONE:
        raise HTTPException(status_code=400, detail="Document analysis must be complete before chatting.")
    
    pdf_text = job.get("pdf_text", "")
    try:
        from services.ai_agent import chat_with_pdf
        answer = await chat_with_pdf(
            content=pdf_text,
            chat_history=request.messages,
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── DOCX download ──────────────────────────────────────────────────────────────
@router.get("/download/{job_id}")
async def download_docx(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    job = jobs[job_id]
    if job["status"] != JobStatus.DONE or not job.get("docx_path"):
        raise HTTPException(status_code=404, detail="Document not ready.")
    return FileResponse(
        path=job["docx_path"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=Path(job["docx_path"]).name,
    )


# ── Background processing pipeline ────────────────────────────────────────────
async def _process_job(job_id: str):
    job = jobs[job_id]
    q: asyncio.Queue = job["queue"]
    steps = job["steps"]
    original_filename = job["original_filename"]

    async def push(status: JobStatus = JobStatus.PROCESSING):
        await q.put(
            ProgressEvent(
                job_id=job_id,
                job_status=status,
                steps=steps,
                error=job.get("error"),
            )
        )

    async def fail(step_id: str, message: str):
        _update_step(steps, step_id, StepStatus.ERROR, message)
        job["status"] = JobStatus.ERROR
        job["error"] = message
        await push(JobStatus.ERROR)

    try:
        job["status"] = JobStatus.PROCESSING

        # ── Step 1: Upload (already done, mark instantly) ──────────────────────
        _update_step(steps, "upload", StepStatus.DONE, "PDF received.")
        await push()

        # ── Step 2: Extract ───────────────────────────────────────────────────
        _update_step(steps, "extract", StepStatus.RUNNING, "Extracting text from PDF…")
        await push()
        try:
            pdf_text = extract_text_from_pdf(job["upload_path"])
            if not pdf_text.strip():
                raise ValueError("No text could be extracted from the PDF.")
        except Exception as e:
            await fail("extract", str(e))
            return
        job["pdf_text"] = pdf_text # Store for chat
        _update_step(steps, "extract", StepStatus.DONE, f"Extracted {len(pdf_text):,} characters.")
        await push()

        # ── Step 3: Analyze ───────────────────────────────────────────────────
        _update_step(steps, "analyze", StepStatus.RUNNING, "Running AI analysis & web research…")
        await push()

        search_messages = []

        async def search_cb(msg: str):
            search_messages.append(msg)
            _update_step(steps, "analyze", StepStatus.RUNNING, msg)
            await push()

        try:
            enhanced_content = await analyze_pdf_content(
                content=pdf_text,
                openai_api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                serpapi_key=settings.SERPAPI_KEY or "",
                progress_callback=search_cb,
            )
        except Exception as e:
            await fail("analyze", f"AI analysis failed: {str(e)}")
            return
        word_count = len(enhanced_content.split())
        _update_step(steps, "analyze", StepStatus.DONE, f"Analysis complete ({word_count:,} words).")
        await push()

        # ── Step 4: Generate DOCX ─────────────────────────────────────────────
        _update_step(steps, "generate", StepStatus.RUNNING, "Generating Word document…")
        await push()
        try:
            output_dir = Path(settings.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = original_filename.replace(".pdf", "")
            date_str = datetime.now().strftime("%Y%m%d")
            docx_filename = f"{base_name}_Enhanced_{date_str}.docx"
            docx_path = str(output_dir / f"{job_id}_{docx_filename}")
            processed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            generate_docx(
                enhanced_content=enhanced_content,
                original_filename=original_filename,
                processed_date=processed_date,
                word_count=word_count,
                output_path=docx_path,
            )
        except Exception as e:
            await fail("generate", f"Document generation failed: {str(e)}")
            return
        job["docx_path"] = docx_path
        _update_step(steps, "generate", StepStatus.DONE, f"Document ready: {docx_filename}")
        await push()

        # ── Step 5: Google Drive ──────────────────────────────────────────────
        view_link = None
        download_link = None
        creds = settings.GOOGLE_SERVICE_ACCOUNT_JSON
        if creds:
            _update_step(steps, "drive", StepStatus.RUNNING, "Uploading to Google Drive…")
            await push()
            try:
                view_link, download_link = upload_to_drive(
                    file_path=docx_path,
                    file_name=docx_filename,
                    credentials_path=creds,
                )
                if view_link:
                    _update_step(steps, "drive", StepStatus.DONE, "Uploaded to Google Drive.")
                else:
                    _update_step(steps, "drive", StepStatus.SKIPPED, "Drive upload skipped (check credentials).")
            except Exception as e:
                _update_step(steps, "drive", StepStatus.SKIPPED, f"Drive upload skipped: {e}")
        else:
            _update_step(steps, "drive", StepStatus.SKIPPED, "No Google Drive credentials configured.")
        await push()

        # ── Finalise ──────────────────────────────────────────────────────────
        result = AnalysisResult(
            job_id=job_id,
            original_filename=original_filename,
            processed_date=processed_date,
            word_count=word_count,
            enhanced_content=enhanced_content,
            docx_download_url=f"/api/download/{job_id}",
            google_drive_view_link=view_link,
            google_drive_download_link=download_link,
            summary=(
                "PDF successfully analyzed and enhanced with AI-powered insights"
                + (" and web research." if settings.SERPAPI_KEY else ".")
            ),
        )
        job["result"] = result
        job["status"] = JobStatus.DONE
        await push(JobStatus.DONE)

    except Exception as e:
        job["status"] = JobStatus.ERROR
        job["error"] = str(e)
        await q.put(
            ProgressEvent(
                job_id=job_id,
                job_status=JobStatus.ERROR,
                steps=steps,
                error=str(e),
            )
        )
