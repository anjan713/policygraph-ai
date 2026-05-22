from pydantic import BaseModel, Field
from typing import Any

class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    status: str
    storage_uri: str
    job_id: str | None = None

class DocumentListItem(BaseModel):
    id: str
    file_name: str
    status: str
    storage_uri: str
    job_id: str | None = None
    error_message: str | None = None
    created_at: str
    processed_at: str | None = None

class EnqueueProcessResponse(BaseModel):
    document_id: str
    status: str
    job_id: str
    message: str

class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
    job_id: str | None = None
    error_message: str | None = None
    processed_at: str | None = None

class ProcessResponse(BaseModel):
    document_id: str
    status: str
    pages_extracted: int
    chunks_created: int
    rules_extracted: int
    graph_nodes: int
    graph_edges: int

class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)

class Citation(BaseModel):
    document_id: str
    chunk_id: str
    page_number: int
    excerpt: str
    score: float | None = None

class QueryResponse(BaseModel):
    query_id: str
    answer: str
    confidence: float
    citations: list[Citation]
    graph_context: list[dict[str, Any]] = []
    answer_mode: str = "rule_based"  # vertex_gemini | rule_based | no_evidence
    model: str | None = None

class CaseValidationRequest(BaseModel):
    procedure: str
    diagnosis: str | None = None
    conservative_treatment_weeks: int | None = None
    symptoms_persist: bool | None = None
    prior_authorization: bool | None = None

class MatchedRule(BaseModel):
    rule_id: str
    procedure: str | None
    decision: str
    requirement_text: str | None
    condition_text: str | None
    confidence: float
    page_number: int | None = None
    excerpt: str | None = None

class CaseValidationResponse(BaseModel):
    decision: str
    reasoning: str
    missing_fields: list[str]
    matched_rules: list[MatchedRule]

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: dict[str, Any]

class GraphEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship: str
    properties: dict[str, Any]

class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
