"""
API routes for meeting management.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingProcessResponse
from app.schemas.extracted_item import ExtractedItemResponse
from app.schemas.task import TaskResponse
from app.services.meeting_service import MeetingService
from app.workers.tasks import process_meeting as process_meeting_task

logger = get_logger(__name__)

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
):
    """Create a new meeting."""
    logger.info(f"Creating meeting: {meeting_data.title}")
    service = MeetingService(db)
    meeting = service.create_meeting(
        title=meeting_data.title,
        ceremony_type=meeting_data.ceremony_type,
        meeting_date=meeting_data.meeting_date,
        tool_type=meeting_data.tool_type,
        project_key=meeting_data.project_key,
    )
    return meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get meeting details by ID."""
    logger.info(f"Fetching meeting {meeting_id}")
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )
    return meeting


@router.post("/{meeting_id}/upload-audio", status_code=status.HTTP_200_OK)
def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload audio file for a meeting."""
    logger.info(f"Uploading audio for meeting {meeting_id}")
    
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )

    # Read file content
    content = file.file.read()
    
    # Validate file type
    if not file.filename or not any(
        file.filename.lower().endswith(ext) for ext in [".mp3", ".wav", ".m4a"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be mp3, wav, or m4a format",
        )

    success = service.upload_audio(meeting_id, content, file.filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload audio file",
        )

    return {"message": "Audio file uploaded successfully"}


@router.post("/{meeting_id}/transcript", status_code=status.HTTP_200_OK)
def add_transcript(
    meeting_id: int,
    transcript_data: dict,
    db: Session = Depends(get_db),
):
    """Add or update transcript for a meeting."""
    logger.info(f"Adding transcript for meeting {meeting_id}")
    
    transcript = transcript_data.get("transcript")
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript text is required",
        )

    service = MeetingService(db)
    meeting = service.add_transcript(meeting_id, transcript)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )

    return {"message": "Transcript added successfully"}


@router.post("/{meeting_id}/process", response_model=MeetingProcessResponse)
def process_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    """Trigger async processing of a meeting."""
    logger.info(f"Processing meeting {meeting_id}")
    
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )

    # Trigger async Celery task
    try:
        task = process_meeting_task.delay(meeting_id)
        logger.info(f"Processing task queued for meeting {meeting_id}: {task.id}")
    except Exception as e:
        logger.error(f"Failed to queue processing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start processing",
        )

    return {
        "started": True,
        "meeting_id": meeting_id,
    }


@router.get("/{meeting_id}/items")
def get_extracted_items(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    """Get extracted items (decisions, blockers) for a meeting."""
    logger.info(f"Fetching extracted items for meeting {meeting_id}")
    
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )

    items = service.get_extracted_items(meeting_id)
    return items


@router.get("/{meeting_id}/tasks", response_model=list[TaskResponse])
def get_meeting_tasks(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    """Get all tasks created from a meeting."""
    logger.info(f"Fetching tasks for meeting {meeting_id}")
    
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found",
        )

    tasks = service.get_tasks(meeting_id)
    return tasks


@router.get("")
def list_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all meetings with pagination."""
    logger.info(f"Listing meetings (skip={skip}, limit={limit})")
    service = MeetingService(db)
    meetings = service.meeting_repo.list_all(skip=skip, limit=limit)
    return meetings
