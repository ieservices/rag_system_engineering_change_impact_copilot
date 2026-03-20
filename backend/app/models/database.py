from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column


class PartStatus(str, Enum):
    ACTIVE = "active"
    OBSOLETE = "obsolete"
    DRAFT = "draft"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    RELEASED = "released"
    OBSOLETE = "obsolete"


class ChangeRequestStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    CLOSED = "closed"


# Part Model
class PartBase(SQLModel):
    part_number: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    material: Optional[str] = None
    weight_kg: Optional[float] = None
    status: PartStatus = PartStatus.ACTIVE
    revision: str = "A"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Part(PartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Assembly Model
class AssemblyBase(SQLModel):
    assembly_number: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    status: PartStatus = PartStatus.ACTIVE
    revision: str = "A"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Assembly(AssemblyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Bill of Materials Entry
class BOMEntryBase(SQLModel):
    assembly_id: int = Field(foreign_key="assembly.id")
    part_id: Optional[int] = Field(default=None, foreign_key="part.id")
    child_assembly_id: Optional[int] = Field(default=None, foreign_key="assembly.id")
    quantity: int = 1
    position: Optional[str] = None


class BOMEntry(BOMEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Document Model
class DocumentBase(SQLModel):
    document_number: str = Field(unique=True, index=True)
    title: str
    document_type: str  # SPEC, TEST, DWG, MANUAL, etc.
    description: Optional[str] = None
    version: str = "1.0"
    status: DocumentStatus = DocumentStatus.DRAFT
    file_path: Optional[str] = None
    content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Document(DocumentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Document-Part Link
class DocumentPartLinkBase(SQLModel):
    document_id: int = Field(foreign_key="document.id")
    part_id: Optional[int] = Field(default=None, foreign_key="part.id")
    assembly_id: Optional[int] = Field(default=None, foreign_key="assembly.id")
    link_type: str = "reference"  # reference, defines, tests, etc.


class DocumentPartLink(DocumentPartLinkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Change Request Model
class ChangeRequestBase(SQLModel):
    cr_number: str = Field(unique=True, index=True)
    title: str
    description: str
    reason: str
    priority: str = "medium"  # low, medium, high, critical
    status: ChangeRequestStatus = ChangeRequestStatus.OPEN
    requestor: str
    affected_parts: Optional[str] = None  # JSON list of part numbers
    affected_assemblies: Optional[str] = None  # JSON list of assembly numbers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None


class ChangeRequest(ChangeRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Specification Model
class SpecificationBase(SQLModel):
    spec_number: str = Field(unique=True, index=True)
    title: str
    description: Optional[str] = None
    category: str  # pressure, temperature, material, etc.
    requirements: str
    version: str = "1.0"
    status: DocumentStatus = DocumentStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Specification(SpecificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Test Report Model
class TestReportBase(SQLModel):
    test_number: str = Field(unique=True, index=True)
    title: str
    description: Optional[str] = None
    test_type: str  # corrosion, pressure, fatigue, etc.
    result: str  # passed, failed, conditional
    test_date: datetime
    tester: str
    findings: Optional[str] = None
    related_spec_id: Optional[int] = Field(default=None, foreign_key="specification.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestReport(TestReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Document Chunk for Vector Search
class DocumentChunkBase(SQLModel):
    document_id: int = Field(foreign_key="document.id")
    chunk_index: int
    content: str
    chunk_metadata: Optional[str] = None  # JSON metadata


class DocumentChunk(DocumentChunkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    embedding: List[float] = Field(sa_column=Column(Vector(1536)))


# Chat Session Model
class ChatSessionBase(SQLModel):
    title: str = "Neue Unterhaltung"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(ChatSessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Chat Message Model
class ChatMessageBase(SQLModel):
    session_id: int = Field(foreign_key="chatsession.id")
    role: str  # "user" or "assistant"
    content: str
    sources: Optional[str] = None  # JSON list of sources
    affected_objects: Optional[str] = None  # JSON object
    confidence: Optional[float] = None
    model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(ChatMessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
