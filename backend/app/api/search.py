from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_session
from app.services.search_service import SearchService

router = APIRouter()


class SearchResult(BaseModel):
    document_id: Optional[int] = None
    document_number: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    score: float = 0.0


@router.get("/", response_model=List[SearchResult])
def search(
    q: str = Query(..., description="Search query"),
    search_type: str = Query("hybrid", description="Search type: vector, keyword, or hybrid"),
    top_k: int = Query(5, description="Number of results to return"),
    session: Session = Depends(get_session)
):
    """Perform search across all documents."""
    search_service = SearchService(session)

    if search_type == "vector":
        results = search_service.vector_search(q, top_k)
    elif search_type == "keyword":
        results = search_service.keyword_search(q, top_k)
    else:
        results = search_service.hybrid_search(q, top_k)

    return [
        SearchResult(
            document_id=r.get("document_id"),
            document_number=r.get("document_number"),
            title=r.get("title"),
            document_type=r.get("document_type"),
            version=r.get("version"),
            status=r.get("status"),
            content=r.get("content", "")[:500],
            score=r.get("score", r.get("combined_score", 0))
        )
        for r in results
    ]


@router.get("/global")
def global_search(
    q: str = Query(..., description="Search query"),
    session: Session = Depends(get_session)
):
    """Search across all entity types."""
    search_service = SearchService(session)

    parts = search_service.search_parts(q)
    assemblies = search_service.search_assemblies(q)
    crs = search_service.search_change_requests(query=q)

    return {
        "parts": [
            {"part_number": p.part_number, "name": p.name, "status": p.status, "material": p.material}
            for p in parts[:10]
        ],
        "assemblies": [
            {"assembly_number": a.assembly_number, "name": a.name, "status": a.status}
            for a in assemblies[:10]
        ],
        "change_requests": [
            {"cr_number": cr.cr_number, "title": cr.title, "status": cr.status, "priority": cr.priority}
            for cr in crs[:10]
        ]
    }
