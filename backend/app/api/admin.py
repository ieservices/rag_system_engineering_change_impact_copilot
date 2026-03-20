from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlmodel import Session, select, text
from typing import Optional
import json
import os
from pathlib import Path

from app.core.database import get_session, init_db
from app.models.database import Document, DocumentChunk
from app.services.embedding_service import embedding_service

router = APIRouter()

# Data directory path (relative to backend folder)
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "documents"


@router.post("/init-db")
def initialize_database():
    """Initialize the database and create tables."""
    try:
        init_db()
        return {"status": "success", "message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_system_stats(session: Session = Depends(get_session)):
    """Get system statistics."""
    from app.models.database import Part, Assembly, ChangeRequest, Specification, TestReport

    stats = {
        "parts_count": session.exec(select(Part)).all().__len__(),
        "assemblies_count": session.exec(select(Assembly)).all().__len__(),
        "documents_count": session.exec(select(Document)).all().__len__(),
        "chunks_count": session.exec(select(DocumentChunk)).all().__len__(),
        "change_requests_count": session.exec(select(ChangeRequest)).all().__len__(),
        "specifications_count": session.exec(select(Specification)).all().__len__(),
        "test_reports_count": session.exec(select(TestReport)).all().__len__(),
    }

    return stats


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    document_number: Optional[str] = None,
    document_type: str = "GENERAL",
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session)
):
    """Upload and ingest a document."""
    content = await file.read()

    # Determine content type and extract text
    if file.filename.endswith('.pdf'):
        # For PDF, we would use pypdf
        from pypdf import PdfReader
        import io
        pdf = PdfReader(io.BytesIO(content))
        text_content = "\n".join([page.extract_text() for page in pdf.pages])
    elif file.filename.endswith('.md') or file.filename.endswith('.txt'):
        text_content = content.decode('utf-8')
    else:
        text_content = content.decode('utf-8', errors='ignore')

    # Create document
    doc_number = document_number or f"DOC-{file.filename.replace('.', '-').upper()}"

    document = Document(
        document_number=doc_number,
        title=file.filename,
        document_type=document_type,
        content=text_content,
        status="draft"
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    # Create chunks and embeddings
    chunks = embedding_service.chunk_text(text_content)

    for i, chunk_text in enumerate(chunks):
        embedding = embedding_service.get_embedding(chunk_text)

        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=i,
            content=chunk_text,
            embedding=embedding,
            metadata=json.dumps({"filename": file.filename, "chunk": i})
        )
        session.add(chunk)

    session.commit()

    return {
        "status": "success",
        "document_id": document.id,
        "document_number": document.document_number,
        "chunks_created": len(chunks)
    }


@router.post("/load-documents")
def load_documents_from_folder(session: Session = Depends(get_session)):
    """Load all documents from the data/documents folder."""
    if not DATA_DIR.exists():
        raise HTTPException(status_code=404, detail=f"Data directory not found: {DATA_DIR}")

    results = []
    errors = []

    for file_path in DATA_DIR.glob("*.md"):
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract document number from filename (e.g., CR-031_... -> CR-031)
            filename = file_path.stem
            doc_number = filename.split("_")[0] if "_" in filename else filename

            # Determine document type from prefix
            doc_type_map = {
                "CR": "CR",
                "SPEC": "SPEC",
                "TEST": "TEST",
                "DWG": "DWG",
                "MANUAL": "MANUAL",
            }
            doc_type = "GENERAL"
            for prefix, dtype in doc_type_map.items():
                if doc_number.startswith(prefix):
                    doc_type = dtype
                    break

            # Check if document already exists
            existing = session.exec(
                select(Document).where(Document.document_number == doc_number)
            ).first()

            if existing:
                # Update existing document
                existing.content = content
                existing.file_path = str(file_path)
                session.add(existing)
                doc = existing
                action = "updated"
            else:
                # Create new document
                doc = Document(
                    document_number=doc_number,
                    title=filename.replace("_", " "),
                    document_type=doc_type,
                    content=content,
                    file_path=str(file_path),
                    status="released"
                )
                session.add(doc)
                action = "created"

            session.commit()
            session.refresh(doc)

            # Delete existing chunks for this document
            session.exec(
                text("DELETE FROM documentchunk WHERE document_id = :doc_id"),
                {"doc_id": doc.id}
            )
            session.commit()

            # Create chunks and embeddings
            chunks = embedding_service.chunk_text(content)
            for i, chunk_text in enumerate(chunks):
                embedding = embedding_service.get_embedding(chunk_text)

                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding,
                    chunk_metadata=json.dumps({"filename": filename, "chunk": i})
                )
                session.add(chunk)

            session.commit()

            results.append({
                "document_number": doc_number,
                "action": action,
                "chunks_created": len(chunks)
            })

        except Exception as e:
            errors.append({
                "file": str(file_path),
                "error": str(e)
            })

    return {
        "status": "success",
        "documents_processed": len(results),
        "results": results,
        "errors": errors
    }


@router.post("/reindex")
def reindex_documents(session: Session = Depends(get_session)):
    """Reindex all documents - recreate embeddings."""
    documents = session.exec(select(Document).where(Document.content.isnot(None))).all()

    total_chunks = 0

    for doc in documents:
        # Delete existing chunks
        session.exec(
            text("DELETE FROM documentchunk WHERE document_id = :doc_id"),
            {"doc_id": doc.id}
        )

        # Create new chunks
        if doc.content:
            chunks = embedding_service.chunk_text(doc.content)

            for i, chunk_text in enumerate(chunks):
                embedding = embedding_service.get_embedding(chunk_text)

                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding,
                    metadata=json.dumps({"document_number": doc.document_number, "chunk": i})
                )
                session.add(chunk)
                total_chunks += 1

    session.commit()

    return {
        "status": "success",
        "documents_processed": len(documents),
        "chunks_created": total_chunks
    }


@router.get("/chunks/{document_id}")
def get_document_chunks(document_id: int, session: Session = Depends(get_session)):
    """Get all chunks for a specific document."""
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = session.exec(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    return {
        "document_id": document_id,
        "document_number": doc.document_number,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "id": c.id,
                "chunk_index": c.chunk_index,
                "content": c.content,
                "has_embedding": c.embedding is not None,
                "embedding_preview": [float(x) for x in c.embedding[:5]] if c.embedding is not None else None  # First 5 dimensions
            }
            for c in chunks
        ]
    }


@router.post("/index-document/{document_id}")
def index_single_document(document_id: int, session: Session = Depends(get_session)):
    """Index a single document - create chunks and embeddings."""
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.content:
        raise HTTPException(status_code=400, detail="Document has no content to index")

    # Delete existing chunks
    existing_chunks = session.exec(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    ).all()
    for chunk in existing_chunks:
        session.delete(chunk)
    session.commit()

    # Create new chunks and embeddings
    errors = []
    chunks_created = 0

    try:
        text_chunks = embedding_service.chunk_text(doc.content)

        for i, chunk_text in enumerate(text_chunks):
            try:
                embedding = embedding_service.get_embedding(chunk_text)

                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding,
                    chunk_metadata=json.dumps({"document_number": doc.document_number, "chunk": i})
                )
                session.add(chunk)
                chunks_created += 1
            except Exception as e:
                errors.append(f"Chunk {i}: {str(e)}")

        session.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")

    return {
        "status": "success" if not errors else "partial",
        "document_id": document_id,
        "document_number": doc.document_number,
        "chunks_created": chunks_created,
        "errors": errors
    }


@router.delete("/clear-data")
def clear_all_data(session: Session = Depends(get_session)):
    """Clear all data from the database. Use with caution!"""
    from app.models.database import (
        Part, Assembly, BOMEntry, Document, ChangeRequest,
        Specification, TestReport, DocumentChunk, DocumentPartLink
    )

    # Delete in order respecting foreign keys
    session.exec(text("DELETE FROM documentchunk"))
    session.exec(text("DELETE FROM documentpartlink"))
    session.exec(text("DELETE FROM bomentry"))
    session.exec(text("DELETE FROM testreport"))
    session.exec(text("DELETE FROM specification"))
    session.exec(text("DELETE FROM changerequest"))
    session.exec(text("DELETE FROM document"))
    session.exec(text("DELETE FROM part"))
    session.exec(text("DELETE FROM assembly"))

    session.commit()

    return {"status": "success", "message": "All data cleared"}
