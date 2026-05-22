from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db import init_db
from .api.documents import router as documents_router
from .api.query import router as query_router
from .api.graph import router as graph_router
from .services.vertex_agent import VertexAgent

init_db()

app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    agent = VertexAgent()
    return {
        "status": "ok",
        "database": "postgresql+pgvector",
        "queue": "redis/rq",
        "graph": "neo4j",
        "storage": "gcs_or_local",
        "ocr": "paddleocr",
        "agent": agent.model if agent.is_available() else "rule-based",
    }

app.include_router(documents_router)
app.include_router(query_router)
app.include_router(graph_router)
