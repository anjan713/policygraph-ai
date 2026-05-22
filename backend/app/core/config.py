import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "PolicyGraph AI")

    # Local runtime paths
    local_upload_dir: str = os.getenv("LOCAL_UPLOAD_DIR", "./data/uploads")

    # PostgreSQL + pgvector. Use docker-compose for local development.
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://policygraph:policygraph@localhost:5432/policygraph",
    )
    vector_dimension: int = int(os.getenv("VECTOR_DIMENSION", "384"))

    # Redis is used for job queue + job/document status cache.
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_name: str = os.getenv("QUEUE_NAME", "policygraph-jobs")

    # Neo4j is used as the knowledge graph for Graph-RAG expansion.
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "policygraph-password")
    use_neo4j: bool = os.getenv("USE_NEO4J", "true").lower() == "true"

    # Google Cloud development/deployment settings
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
    gcp_region: str = os.getenv("GCP_REGION", "us-central1")
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT_ID", ""))
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # Both local and GCS modes are supported. In production, keep USE_GCS=true.
    use_gcs: bool = os.getenv("USE_GCS", "false").lower() == "true"
    gcs_bucket: str = os.getenv("GCS_BUCKET", "")
    gcs_prefix: str = os.getenv("GCS_PREFIX", "policygraph/uploads")

    # OCR settings. This architecture intentionally always uses PaddleOCR.
    ocr_engine: str = os.getenv("OCR_ENGINE", "paddleocr")
    paddleocr_lang: str = os.getenv("PADDLEOCR_LANG", "en")
    ocr_render_dpi: int = int(os.getenv("OCR_RENDER_DPI", "200"))

    # Optional GCP AI settings for production upgrades.
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", os.getenv("GCP_REGION", "us-central1"))
    vertex_embedding_model: str = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-005")
    vertex_llm_model: str = os.getenv("VERTEX_LLM_MODEL", "gemini-1.5-flash")

    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    def ensure_dirs(self) -> None:
        Path(self.local_upload_dir).mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
