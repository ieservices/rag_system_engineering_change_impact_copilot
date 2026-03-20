from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
import json

from app.core.database import get_session
from app.models.database import ChangeRequest, Part, Assembly, Document
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=List[ChangeRequest])
def list_change_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all change requests with optional filtering."""
    statement = select(ChangeRequest)

    if status:
        statement = statement.where(ChangeRequest.status == status)
    if priority:
        statement = statement.where(ChangeRequest.priority == priority)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/open")
def list_open_change_requests(session: Session = Depends(get_session)):
    """List all open change requests."""
    statement = select(ChangeRequest).where(
        ChangeRequest.status.in_(["open", "in_progress", "review"])
    ).order_by(ChangeRequest.created_at.desc())

    return list(session.exec(statement))


@router.get("/{cr_number}", response_model=ChangeRequest)
def get_change_request(cr_number: str, session: Session = Depends(get_session)):
    """Get a specific change request by number."""
    cr = session.exec(
        select(ChangeRequest).where(ChangeRequest.cr_number == cr_number)
    ).first()

    if not cr:
        raise HTTPException(status_code=404, detail=f"Change request {cr_number} not found")

    return cr


@router.get("/{cr_number}/impact")
def get_change_request_impact(cr_number: str, session: Session = Depends(get_session)):
    """Get full impact analysis for a change request."""
    cr = session.exec(
        select(ChangeRequest).where(ChangeRequest.cr_number == cr_number)
    ).first()

    if not cr:
        raise HTTPException(status_code=404, detail=f"Change request {cr_number} not found")

    # Parse affected parts and assemblies
    affected_parts = []
    affected_assemblies = []

    if cr.affected_parts:
        try:
            part_numbers = json.loads(cr.affected_parts)
            for pn in part_numbers:
                part = session.exec(
                    select(Part).where(Part.part_number == pn)
                ).first()
                if part:
                    affected_parts.append(part)
        except json.JSONDecodeError:
            pass

    if cr.affected_assemblies:
        try:
            assembly_numbers = json.loads(cr.affected_assemblies)
            for an in assembly_numbers:
                assembly = session.exec(
                    select(Assembly).where(Assembly.assembly_number == an)
                ).first()
                if assembly:
                    affected_assemblies.append(assembly)
        except json.JSONDecodeError:
            pass

    # Find related documents (documents that reference affected parts/assemblies)
    search_service = SearchService(session)
    related_docs = []

    for part in affected_parts:
        impact = search_service.get_part_impact(part.part_number)
        related_docs.extend(impact.get("related_documents", []))

    for assembly in affected_assemblies:
        impact = search_service.get_assembly_impact(assembly.assembly_number)
        related_docs.extend(impact.get("related_documents", []))

    # Deduplicate documents
    seen_doc_ids = set()
    unique_docs = []
    for doc in related_docs:
        if doc.id not in seen_doc_ids:
            seen_doc_ids.add(doc.id)
            unique_docs.append(doc)

    return {
        "change_request": cr,
        "affected_parts": affected_parts,
        "affected_assemblies": affected_assemblies,
        "related_documents": unique_docs
    }


@router.get("/search/")
def search_change_requests(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = None,
    part_number: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Search for change requests."""
    search_service = SearchService(session)
    return search_service.search_change_requests(
        query=q,
        status=status,
        part_number=part_number
    )
