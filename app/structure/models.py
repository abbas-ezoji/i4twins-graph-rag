from typing import Any

from pydantic import BaseModel, Field


class Entity(BaseModel):
    text: str
    entity_type: str
    normalized: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Fact(BaseModel):
    subject: str
    predicate: str
    value: Any
    unit: str | None = None
    source_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relation(BaseModel):
    source: str
    relation: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StructuredDocument(BaseModel):
    document_id: str
    title: str = ""
    text: str

    entities: list[Entity] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    relations: list[Relation] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)