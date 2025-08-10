import json
from typing import Any
import uuid

import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase, relationship, Mapped, mapped_column
)
from pgvector.sqlalchemy import Vector


class VectorBase(DeclarativeBase):
    pass


class CollectionStore(VectorBase):
    __tablename__ = "vector_master"

    collection_id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        nullable=False,
    )
    collection_name: Mapped[str] = mapped_column(
        sqlalchemy.String(100),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        sqlalchemy.String(255),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Flag indicating whether the collection is deleted. Default is False."
    )
    created_at: Mapped[sqlalchemy.DateTime] = mapped_column(
        sqlalchemy.DateTime,
        default=sqlalchemy.func.now(),
    )
    updated_at: Mapped[sqlalchemy.DateTime] = mapped_column(
        sqlalchemy.DateTime,
        default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )

    embeddings_relation = relationship(
        "EmbeddingStore",
        back_populates="collection_relation",
        passive_deletes=True,
    )

    def marshal_metadata(self, dictlike: Any) -> str:
        return json.dumps(dictlike, ensure_ascii=False)

    def unmarshal_metadata(self, json_str: str) -> dict[str, Any]:
        return json.loads(json_str)


class EmbeddingStore(VectorBase):
    __tablename__ = "vector_detail"

    id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    collection_id: Mapped[str] = mapped_column(
        sqlalchemy.String(36),
        sqlalchemy.ForeignKey(
            f"{CollectionStore.__tablename__}.collection_id",
            ondelete="CASCADE",
        ),
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        doc="The vector embedding associated with this document."
    )
    document: Mapped[str] = mapped_column(
        sqlalchemy.String,
        doc="The content of the document associated with this embedding."
    )
    is_deleted: Mapped[bool] = mapped_column(
        sqlalchemy.Boolean,
        default=False,
        doc="Flag indicating whether the collection is deleted. Default is False."
    )
    created_at: Mapped[sqlalchemy.DateTime] = mapped_column(
        sqlalchemy.DateTime,
        default=sqlalchemy.func.now(),
    )
    updated_at: Mapped[sqlalchemy.DateTime] = mapped_column(
        sqlalchemy.DateTime,
        default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )

    collection_relation = relationship(
        CollectionStore, 
        back_populates="embeddings_relation"
    )


def create_vector_all(engine: sqlalchemy.Engine):
    VectorBase.metadata.create_all(engine)


def drop_vector_all(engine: sqlalchemy.Engine):
    VectorBase.metadata.drop_all(engine)