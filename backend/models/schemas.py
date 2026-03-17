from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    SKIPPED = "skipped"


class PipelineStep(BaseModel):
    id: str
    label: str
    status: StepStatus = StepStatus.PENDING
    message: Optional[str] = None


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class ProgressEvent(BaseModel):
    job_id: str
    job_status: JobStatus
    steps: List[PipelineStep]
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    job_id: str
    original_filename: str
    processed_date: str
    version: str = "Enhanced v1.0"
    word_count: int
    enhanced_content: str
    docx_download_url: str
    google_drive_view_link: Optional[str] = None
    google_drive_download_link: Optional[str] = None
    summary: str


PIPELINE_STEPS = [
    PipelineStep(id="upload",    label="Uploading PDF"),
    PipelineStep(id="extract",   label="Extracting Content"),
    PipelineStep(id="analyze",   label="AI Analysis & Web Research"),
    PipelineStep(id="generate",  label="Generating Document"),
    PipelineStep(id="drive",     label="Uploading to Google Drive"),
]
