from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.core.database import get_session
from app.models.database import Assembly, BOMEntry, Part
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=List[Assembly])
def list_assemblies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all assemblies with optional filtering."""
    statement = select(Assembly)

    if status:
        statement = statement.where(Assembly.status == status)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/{assembly_number}", response_model=Assembly)
def get_assembly(assembly_number: str, session: Session = Depends(get_session)):
    """Get a specific assembly by number."""
    assembly = session.exec(
        select(Assembly).where(Assembly.assembly_number == assembly_number)
    ).first()

    if not assembly:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_number} not found")

    return assembly


@router.get("/{assembly_number}/bom")
def get_assembly_bom(assembly_number: str, session: Session = Depends(get_session)):
    """Get bill of materials for an assembly."""
    assembly = session.exec(
        select(Assembly).where(Assembly.assembly_number == assembly_number)
    ).first()

    if not assembly:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_number} not found")

    # Get BOM entries
    bom_entries = session.exec(
        select(BOMEntry).where(BOMEntry.assembly_id == assembly.id)
    ).all()

    result = []
    for entry in bom_entries:
        item = {
            "quantity": entry.quantity,
            "position": entry.position
        }

        if entry.part_id:
            part = session.get(Part, entry.part_id)
            if part:
                item["type"] = "part"
                item["part_number"] = part.part_number
                item["name"] = part.name
                item["material"] = part.material

        if entry.child_assembly_id:
            child_assembly = session.get(Assembly, entry.child_assembly_id)
            if child_assembly:
                item["type"] = "assembly"
                item["assembly_number"] = child_assembly.assembly_number
                item["name"] = child_assembly.name

        result.append(item)

    return {
        "assembly": assembly,
        "bom": result
    }


@router.get("/{assembly_number}/impact")
def get_assembly_impact(assembly_number: str, session: Session = Depends(get_session)):
    """Get impact analysis for an assembly."""
    search_service = SearchService(session)
    return search_service.get_assembly_impact(assembly_number)


@router.get("/search/")
def search_assemblies(
    q: str = Query(..., description="Search query"),
    session: Session = Depends(get_session)
):
    """Search for assemblies."""
    search_service = SearchService(session)
    assemblies = search_service.search_assemblies(q)
    return assemblies
