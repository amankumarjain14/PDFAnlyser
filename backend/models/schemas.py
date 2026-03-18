from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    answer: str


class VisitInfo(BaseModel):
    ip: str
    user_agent: str
    timestamp: str


class UploadInfo(BaseModel):
    filename: str
    job_id: str
    timestamp: str
    ip: str
    status: Optional[str] = "SUCCESS"
    processing_time: Optional[float] = None


class DailyTrend(BaseModel):
    date: str
    visits: int
    uploads: int


class AdminStats(BaseModel):
    total_visits: int
    total_unique_visitors: int
    total_uploads: int
    conversion_rate: float = 0.0
    avg_processing_time: float = 0.0
    daily_trends: List[DailyTrend] = []
    recent_visits: List[VisitInfo]
    recent_uploads: List[UploadInfo]


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
