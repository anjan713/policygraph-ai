from fastapi import APIRouter
from ..schemas import QueryRequest, QueryResponse, CaseValidationRequest, CaseValidationResponse
from ..services.query_service import QueryService
from ..services.validation_service import ValidationService

router = APIRouter(prefix="/api", tags=["query"])

@router.post("/query", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    return QueryService().answer(request.question, top_k=request.top_k)

@router.post("/validate-case", response_model=CaseValidationResponse)
def validate_case(request: CaseValidationRequest):
    return ValidationService().validate(request.model_dump())
