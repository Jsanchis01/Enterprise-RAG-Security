import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    clearance_level: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Provenance metadata required for knowledge poisoning defense
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="official_policy")
    issuing_department: Mapped[str] = mapped_column(String(50), nullable=False)
    author_role: Mapped[str] = mapped_column(String(50), nullable=False)
    source_authority: Mapped[str] = mapped_column(String(50), nullable=False, default="authoritative")
    trust_status: Mapped[str] = mapped_column(String(50), nullable=False, default="certified")

    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    clearance_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Replicated provenance metadata on chunk level for vector filtering
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="official_policy")
    issuing_department: Mapped[str] = mapped_column(String(50), nullable=False)
    author_role: Mapped[str] = mapped_column(String(50), nullable=False)
    source_authority: Mapped[str] = mapped_column(String(50), nullable=False, default="authoritative")
    trust_status: Mapped[str] = mapped_column(String(50), nullable=False, default="certified")

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
