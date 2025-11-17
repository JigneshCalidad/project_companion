"""Ask/query routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.graph_service import GraphService


router = APIRouter(prefix="/api/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: dict
    matches: list
    related: list
    total_matches: int


def get_graph_service(knowledge_store: Optional[object] = None) -> GraphService:
    """Dependency to get graph service."""
    from knowledge.store import KnowledgeStore
    if knowledge_store is None:
        knowledge_store = KnowledgeStore()
    return GraphService(knowledge_store)


@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    graph_service: GraphService = Depends(get_graph_service)
):
    """Ask a question about the codebase."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = graph_service.query(request.question)
        return AskResponse(
            question=result["question"],
            answer=result,
            matches=result.get("matches", []),
            related=result.get("related", []),
            total_matches=result.get("total_matches", 0)
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

