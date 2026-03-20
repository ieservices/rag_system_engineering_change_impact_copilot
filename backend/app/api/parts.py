from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.core.database import get_session
from app.models.database import Part
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=List[Part])
def list_parts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    material: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all parts with optional filtering."""
    statement = select(Part)

    if status:
        statement = statement.where(Part.status == status)
    if material:
        statement = statement.where(Part.material.ilike(f"%{material}%"))

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/{part_number}", response_model=Part)
def get_part(part_number: str, session: Session = Depends(get_session)):
    """Get a specific part by part number."""
    part = session.exec(
        select(Part).where(Part.part_number == part_number)
    ).first()

    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_number} not found")

    return part


@router.get("/{part_number}/impact")
def get_part_impact(part_number: str, session: Session = Depends(get_session)):
    """Get impact analysis for a part."""
    search_service = SearchService(session)
    return search_service.get_part_impact(part_number)


@router.get("/search/")
def search_parts(
    q: str = Query(..., description="Search query"),
    session: Session = Depends(get_session)
):
    """Search for parts."""
    search_service = SearchService(session)
    parts = search_service.search_parts(q)
    return parts
