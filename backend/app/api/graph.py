from fastapi import APIRouter
from ..schemas import GraphResponse
from ..services.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("", response_model=GraphResponse)
def get_graph():
    return GraphService().get_graph()
