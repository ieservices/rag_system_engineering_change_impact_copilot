from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional

from app.core.database import get_session
from app.models.database import Document, Specification, TestReport, DocumentPartLink

router = APIRouter()


@router.get("/", response_model=List[Document])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all documents with optional filtering."""
    statement = select(Document)

    if document_type:
        statement = statement.where(Document.document_type == document_type)
    if status:
        statement = statement.where(Document.status == status)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/{document_number}")
def get_document(document_number: str, session: Session = Depends(get_session)):
    """Get a specific document by number."""
    document = session.exec(
        select(Document).where(Document.document_number == document_number)
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_number} not found")

    return document


@router.get("/{document_number}/links")
def get_document_links(document_number: str, session: Session = Depends(get_session)):
    """Get all parts and assemblies linked to a document."""
    document = session.exec(
        select(Document).where(Document.document_number == document_number)
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_number} not found")

    links = session.exec(
        select(DocumentPartLink).where(DocumentPartLink.document_id == document.id)
    ).all()

    return {
        "document": document,
        "links": [
            {
                "part_id": link.part_id,
                "assembly_id": link.assembly_id,
                "link_type": link.link_type
            }
            for link in links
        ]
    }


# Specifications endpoints
@router.get("/specifications/", response_model=List[Specification])
def list_specifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all specifications."""
    statement = select(Specification)

    if category:
        statement = statement.where(Specification.category == category)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/specifications/{spec_number}", response_model=Specification)
def get_specification(spec_number: str, session: Session = Depends(get_session)):
    """Get a specific specification."""
    spec = session.exec(
        select(Specification).where(Specification.spec_number == spec_number)
    ).first()

    if not spec:
        raise HTTPException(status_code=404, detail=f"Specification {spec_number} not found")

    return spec


# Test Reports endpoints
@router.get("/test-reports/", response_model=List[TestReport])
def list_test_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    test_type: Optional[str] = None,
    result: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all test reports."""
    statement = select(TestReport)

    if test_type:
        statement = statement.where(TestReport.test_type == test_type)
    if result:
        statement = statement.where(TestReport.result == result)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


@router.get("/test-reports/{test_number}", response_model=TestReport)
def get_test_report(test_number: str, session: Session = Depends(get_session)):
    """Get a specific test report."""
    report = session.exec(
        select(TestReport).where(TestReport.test_number == test_number)
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail=f"Test report {test_number} not found")

    return report
