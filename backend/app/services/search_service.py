from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, text
from sqlalchemy import or_, and_
import json

from app.models.database import (
    Part, Assembly, BOMEntry, Document, ChangeRequest,
    Specification, TestReport, DocumentChunk, DocumentPartLink
)
from app.services.embedding_service import embedding_service
from app.core.config import settings


class SearchService:
    def __init__(self, session: Session):
        self.session = session

    def vector_search(
        self,
        query: str,
        top_k: int = None,
        document_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        top_k = top_k or settings.TOP_K_RESULTS

        # Get query embedding
        query_embedding = embedding_service.get_embedding(query)

        # Build vector search query
        sql = text("""
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                dc.chunk_metadata,
                d.document_number,
                d.title,
                d.document_type,
                d.version,
                d.status,
                1 - (dc.embedding <=> :embedding) as score
            FROM documentchunk dc
            JOIN document d ON dc.document_id = d.id
            WHERE 1=1
            ORDER BY dc.embedding <=> :embedding
            LIMIT :limit
        """)

        result = self.session.execute(
            sql,
            {"embedding": str(query_embedding), "limit": top_k}
        )

        return [
            {
                "chunk_id": row.id,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "metadata": json.loads(row.chunk_metadata) if row.chunk_metadata else {},
                "document_number": row.document_number,
                "title": row.title,
                "document_type": row.document_type,
                "version": row.version,
                "status": row.status,
                "score": float(row.score)
            }
            for row in result
        ]

    def keyword_search(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search on documents."""
        top_k = top_k or settings.TOP_K_RESULTS

        # Simple LIKE search on document content
        sql = text("""
            SELECT
                d.id,
                d.document_number,
                d.title,
                d.document_type,
                d.version,
                d.status,
                d.content,
                0.5 as score
            FROM document d
            WHERE LOWER(d.content) LIKE LOWER(:query)
               OR LOWER(d.title) LIKE LOWER(:query)
               OR LOWER(d.description) LIKE LOWER(:query)
            LIMIT :limit
        """)

        result = self.session.execute(
            sql,
            {"query": f"%{query}%", "limit": top_k}
        )

        return [
            {
                "document_id": row.id,
                "document_number": row.document_number,
                "title": row.title,
                "document_type": row.document_type,
                "version": row.version,
                "status": row.status,
                "content": row.content[:500] if row.content else "",
                "score": 0.5
            }
            for row in result
        ]

    def hybrid_search(
        self,
        query: str,
        top_k: int = None,
        alpha: float = 0.7  # Weight for vector search
    ) -> List[Dict[str, Any]]:
        """Combine vector and keyword search results."""
        top_k = top_k or settings.TOP_K_RESULTS

        # Get results from both methods
        vector_results = self.vector_search(query, top_k * 2)
        keyword_results = self.keyword_search(query, top_k * 2)

        # Combine and deduplicate
        combined = {}
        for result in vector_results:
            key = result.get("document_id")
            if key:
                result["combined_score"] = result["score"] * alpha
                combined[key] = result

        for result in keyword_results:
            key = result.get("document_id")
            if key in combined:
                combined[key]["combined_score"] += result["score"] * (1 - alpha)
            elif key:
                result["combined_score"] = result["score"] * (1 - alpha)
                combined[key] = result

        # Sort by combined score and return top_k
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x.get("combined_score", 0),
            reverse=True
        )

        return sorted_results[:top_k]

    def search_parts(self, query: str) -> List[Part]:
        """Search for parts by number, name, or material."""
        statement = select(Part).where(
            or_(
                Part.part_number.ilike(f"%{query}%"),
                Part.name.ilike(f"%{query}%"),
                Part.material.ilike(f"%{query}%"),
                Part.description.ilike(f"%{query}%")
            )
        )
        return list(self.session.exec(statement))

    def search_assemblies(self, query: str) -> List[Assembly]:
        """Search for assemblies by number or name."""
        statement = select(Assembly).where(
            or_(
                Assembly.assembly_number.ilike(f"%{query}%"),
                Assembly.name.ilike(f"%{query}%"),
                Assembly.description.ilike(f"%{query}%")
            )
        )
        return list(self.session.exec(statement))

    def search_change_requests(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        part_number: Optional[str] = None
    ) -> List[ChangeRequest]:
        """Search for change requests."""
        conditions = []

        if query:
            conditions.append(
                or_(
                    ChangeRequest.cr_number.ilike(f"%{query}%"),
                    ChangeRequest.title.ilike(f"%{query}%"),
                    ChangeRequest.description.ilike(f"%{query}%")
                )
            )

        if status:
            conditions.append(ChangeRequest.status == status)

        if part_number:
            conditions.append(
                ChangeRequest.affected_parts.ilike(f"%{part_number}%")
            )

        statement = select(ChangeRequest)
        if conditions:
            statement = statement.where(and_(*conditions))

        return list(self.session.exec(statement))

    def get_part_impact(self, part_number: str) -> Dict[str, Any]:
        """Get full impact analysis for a part."""
        # Find the part
        part = self.session.exec(
            select(Part).where(Part.part_number == part_number)
        ).first()

        if not part:
            return {"error": f"Teil {part_number} nicht gefunden"}

        # Find assemblies containing this part
        bom_entries = self.session.exec(
            select(BOMEntry).where(BOMEntry.part_id == part.id)
        ).all()

        assembly_ids = [entry.assembly_id for entry in bom_entries]
        assemblies = []
        if assembly_ids:
            assemblies = list(self.session.exec(
                select(Assembly).where(Assembly.id.in_(assembly_ids))
            ))

        # Find linked documents
        doc_links = self.session.exec(
            select(DocumentPartLink).where(DocumentPartLink.part_id == part.id)
        ).all()

        doc_ids = [link.document_id for link in doc_links]
        documents = []
        if doc_ids:
            documents = list(self.session.exec(
                select(Document).where(Document.id.in_(doc_ids))
            ))

        # Find change requests
        change_requests = self.session.exec(
            select(ChangeRequest).where(
                ChangeRequest.affected_parts.ilike(f"%{part_number}%")
            )
        ).all()

        return {
            "part": part,
            "affected_assemblies": assemblies,
            "related_documents": documents,
            "change_requests": list(change_requests),
            "bom_entries": bom_entries
        }

    def get_assembly_impact(self, assembly_number: str) -> Dict[str, Any]:
        """Get full impact analysis for an assembly."""
        assembly = self.session.exec(
            select(Assembly).where(Assembly.assembly_number == assembly_number)
        ).first()

        if not assembly:
            return {"error": f"Baugruppe {assembly_number} nicht gefunden"}

        # Find parts in this assembly
        bom_entries = self.session.exec(
            select(BOMEntry).where(BOMEntry.assembly_id == assembly.id)
        ).all()

        part_ids = [entry.part_id for entry in bom_entries if entry.part_id]
        parts = []
        if part_ids:
            parts = list(self.session.exec(
                select(Part).where(Part.id.in_(part_ids))
            ))

        # Find parent assemblies
        parent_entries = self.session.exec(
            select(BOMEntry).where(BOMEntry.child_assembly_id == assembly.id)
        ).all()

        parent_ids = [entry.assembly_id for entry in parent_entries]
        parent_assemblies = []
        if parent_ids:
            parent_assemblies = list(self.session.exec(
                select(Assembly).where(Assembly.id.in_(parent_ids))
            ))

        # Find linked documents
        doc_links = self.session.exec(
            select(DocumentPartLink).where(DocumentPartLink.assembly_id == assembly.id)
        ).all()

        doc_ids = [link.document_id for link in doc_links]
        documents = []
        if doc_ids:
            documents = list(self.session.exec(
                select(Document).where(Document.id.in_(doc_ids))
            ))

        # Find change requests
        change_requests = self.session.exec(
            select(ChangeRequest).where(
                ChangeRequest.affected_assemblies.ilike(f"%{assembly_number}%")
            )
        ).all()

        return {
            "assembly": assembly,
            "parts": parts,
            "parent_assemblies": parent_assemblies,
            "related_documents": documents,
            "change_requests": list(change_requests)
        }
