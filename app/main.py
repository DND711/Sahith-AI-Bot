from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, schemas
from .database import init_db
from .dependencies import get_db
from .services.processing import TranscriptProcessor

app = FastAPI(title="Sahith AI Bot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health", response_model=schemas.HealthResponse)
def health() -> schemas.HealthResponse:
    return schemas.HealthResponse(status="ok", version=app.version)


@app.post("/meetings", response_model=schemas.MeetingRead, status_code=201)
def create_meeting(
    meeting: schemas.MeetingCreate, db: Session = Depends(get_db)
) -> schemas.MeetingRead:
    db_meeting = models.Meeting(
        title=meeting.title,
        scheduled_start=meeting.scheduled_start,
        description=meeting.description,
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


@app.get("/meetings", response_model=List[schemas.MeetingRead])
def list_meetings(db: Session = Depends(get_db)) -> List[schemas.MeetingRead]:
    return db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).all()


@app.get("/meetings/{meeting_id}", response_model=schemas.MeetingDetail)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)) -> schemas.MeetingDetail:
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@app.post(
    "/meetings/{meeting_id}/transcript",
    response_model=schemas.SummaryResponse,
    status_code=201,
)
def upload_transcript(
    meeting_id: int,
    payload: schemas.TranscriptIngestionRequest,
    db: Session = Depends(get_db),
) -> schemas.SummaryResponse:
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    processor = TranscriptProcessor(speaker_prefix=payload.speaker_prefix or "Speaker")
    segments = processor.segment_transcript(payload.transcript_text)
    insights = processor.build_insights(payload.transcript_text)

    db.query(models.TranscriptSegment).filter_by(meeting_id=meeting_id).delete()
    db.query(models.ActionItem).filter_by(meeting_id=meeting_id).delete()
    db.query(models.Suggestion).filter_by(meeting_id=meeting_id).delete()
    db.query(models.Summary).filter_by(meeting_id=meeting_id).delete()

    for idx, (speaker, content) in enumerate(segments, start=1):
        db_segment = models.TranscriptSegment(
            meeting_id=meeting_id, position=idx, speaker=speaker, content=content
        )
        db.add(db_segment)

    db_summary = models.Summary(
        meeting_id=meeting_id,
        tldr=insights.tldr,
        discussion=insights.discussion,
        decisions=insights.decisions,
        risks=insights.risks,
    )
    db.add(db_summary)

    for action in insights.action_items:
        db.add(models.ActionItem(meeting_id=meeting_id, description=action))

    for suggestion in insights.suggestions:
        db.add(models.Suggestion(meeting_id=meeting_id, content=suggestion))

    db.commit()
    db.refresh(meeting)

    return schemas.SummaryResponse(
        meeting=meeting,
        summary=meeting.summary,
        action_items=meeting.action_items,
        suggestions=meeting.suggestions,
    )


@app.post(
    "/meetings/{meeting_id}/audio",
    response_model=schemas.SummaryResponse,
    status_code=201,
)
def upload_audio_placeholder(
    meeting_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> schemas.SummaryResponse:
    contents = file.file.read().decode("utf-8")
    payload = schemas.TranscriptIngestionRequest(transcript_text=contents)
    return upload_transcript(meeting_id=meeting_id, payload=payload, db=db)


@app.get(
    "/meetings/{meeting_id}/summary",
    response_model=schemas.SummaryResponse,
)
def get_summary(meeting_id: int, db: Session = Depends(get_db)) -> schemas.SummaryResponse:
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return schemas.SummaryResponse(
        meeting=meeting,
        summary=meeting.summary,
        action_items=meeting.action_items,
        suggestions=meeting.suggestions,
    )
