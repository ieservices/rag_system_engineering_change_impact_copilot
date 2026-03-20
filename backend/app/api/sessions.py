from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.core.database import get_session
from app.models.database import ChatSession, ChatMessage

router = APIRouter()


class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[dict]] = None
    affected_objects: Optional[dict] = None
    confidence: Optional[float] = None
    model: Optional[str] = None
    created_at: datetime


class SessionDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


class UpdateSessionRequest(BaseModel):
    title: str


@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """List all chat sessions, most recent first."""
    sessions = session.exec(
        select(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    result = []
    for s in sessions:
        msg_count = len(session.exec(
            select(ChatMessage).where(ChatMessage.session_id == s.id)
        ).all())

        result.append(SessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=msg_count
        ))

    return result


@router.post("/", response_model=SessionResponse)
def create_session(session: Session = Depends(get_session)):
    """Create a new chat session."""
    chat_session = ChatSession(
        title="Neue Unterhaltung",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)

    return SessionResponse(
        id=chat_session.id,
        title=chat_session.title,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        message_count=0
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(session_id: int, session: Session = Depends(get_session)):
    """Get a chat session with all its messages."""
    chat_session = session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    ).all()

    message_responses = []
    for msg in messages:
        sources = json.loads(msg.sources) if msg.sources else None
        affected = json.loads(msg.affected_objects) if msg.affected_objects else None

        message_responses.append(MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=sources,
            affected_objects=affected,
            confidence=msg.confidence,
            model=msg.model,
            created_at=msg.created_at
        ))

    return SessionDetailResponse(
        id=chat_session.id,
        title=chat_session.title,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        messages=message_responses
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    request: UpdateSessionRequest,
    session: Session = Depends(get_session)
):
    """Update a chat session (e.g., rename it)."""
    chat_session = session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_session.title = request.title
    chat_session.updated_at = datetime.utcnow()
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)

    msg_count = len(session.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
    ).all())

    return SessionResponse(
        id=chat_session.id,
        title=chat_session.title,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        message_count=msg_count
    )


@router.delete("/{session_id}")
def delete_session(session_id: int, session: Session = Depends(get_session)):
    """Delete a chat session and all its messages."""
    chat_session = session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete all messages first
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
    ).all()
    for msg in messages:
        session.delete(msg)

    # Delete the session
    session.delete(chat_session)
    session.commit()

    return {"status": "success", "message": "Session deleted"}
