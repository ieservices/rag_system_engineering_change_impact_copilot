from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.core.database import get_session
from app.services.search_service import SearchService
from app.services.rag_service import rag_service
from app.models.database import ChatSession, ChatMessage as ChatMessageModel

router = APIRouter()


class ChatMessageSchema(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    sources: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    affected_objects: Dict[str, Any]
    confidence: float
    model: str
    session_id: Optional[int] = None


EXAMPLE_QUERIES = [
    "Welche Dokumente sind von einer Änderung an Baugruppe BG-240 betroffen?",
    "Zeige mir alle Spezifikationen und Prüfberichte für Ventil V-202.",
    "Welche Risiken bestehen, wenn Material M-17 ersetzt wird?",
    "Welche offenen Änderungen betreffen Bauteile aus Edelstahl?",
    "Welche Baugruppen sind betroffen, wenn V-202 ersetzt wird?",
    "Zeige Prüfberichte für Bauteile aus 1.4404.",
    "Welche offenen CRs betreffen BG-240?"
]


@router.get("/examples")
def get_example_queries() -> List[str]:
    """Get example queries for the UI."""
    return EXAMPLE_QUERIES


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, session: Session = Depends(get_session)):
    """Process a chat message and return AI response with sources."""
    search_service = SearchService(session)

    # Handle session - create new if not provided
    chat_session = None
    if request.session_id:
        chat_session = session.get(ChatSession, request.session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create a new session
        chat_session = ChatSession(
            title="Neue Unterhaltung",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)

    # Save user message
    user_message = ChatMessageModel(
        session_id=chat_session.id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)

    # Perform hybrid search
    search_results = search_service.hybrid_search(request.message)

    # Find affected objects
    affected_objects = {
        "parts": [],
        "assemblies": [],
        "change_requests": [],
        "specifications": []
    }

    # Search for mentioned parts
    parts = search_service.search_parts(request.message)
    affected_objects["parts"] = [
        {"part_number": p.part_number, "name": p.name, "status": p.status}
        for p in parts[:5]
    ]

    # Search for mentioned assemblies
    assemblies = search_service.search_assemblies(request.message)
    affected_objects["assemblies"] = [
        {"assembly_number": a.assembly_number, "name": a.name, "status": a.status}
        for a in assemblies[:5]
    ]

    # Search for related change requests
    crs = search_service.search_change_requests(query=request.message)
    affected_objects["change_requests"] = [
        {"cr_number": cr.cr_number, "title": cr.title, "status": cr.status}
        for cr in crs[:5]
    ]

    # Generate AI response
    response = rag_service.generate_response(
        query=request.message,
        context=search_results,
        conversation_history=request.conversation_history
    )

    # Calculate confidence based on search results
    if search_results:
        avg_score = sum(r.get("score", 0) for r in search_results) / len(search_results)
        confidence = min(avg_score * 1.2, 1.0)  # Scale up slightly, cap at 1.0
    else:
        confidence = 0.3

    sources_list = [
        {
            "document_number": s.get("document_number"),
            "title": s.get("title"),
            "version": s.get("version"),
            "status": s.get("status"),
            "document_type": s.get("document_type"),
            "excerpt": s.get("content", "")[:300],
            "score": s.get("score", 0)
        }
        for s in search_results
    ]

    # Save assistant message
    assistant_message = ChatMessageModel(
        session_id=chat_session.id,
        role="assistant",
        content=response["answer"],
        sources=json.dumps(sources_list),
        affected_objects=json.dumps(affected_objects),
        confidence=confidence,
        model=response["model"],
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)

    # Update session title based on first user message if it's still default
    if chat_session.title == "Neue Unterhaltung":
        # Use first 50 chars of the message as title
        chat_session.title = request.message[:50] + ("..." if len(request.message) > 50 else "")

    chat_session.updated_at = datetime.utcnow()
    session.add(chat_session)
    session.commit()

    return ChatResponse(
        answer=response["answer"],
        sources=sources_list,
        affected_objects=affected_objects,
        confidence=confidence,
        model=response["model"],
        session_id=chat_session.id
    )


@router.post("/impact/{object_type}/{object_id}")
def get_impact_analysis(
    object_type: str,
    object_id: str,
    session: Session = Depends(get_session)
):
    """Get impact analysis for a specific object."""
    search_service = SearchService(session)

    if object_type == "part":
        return search_service.get_part_impact(object_id)
    elif object_type == "assembly":
        return search_service.get_assembly_impact(object_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown object type: {object_type}")
