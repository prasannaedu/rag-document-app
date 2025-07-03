from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.services.rag_service import RAGService
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()
rag_service = RAGService()

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[str]

@router.get("/rag/status", summary="Get RAG service status")
def rag_status():
    return rag_service.get_status()

@router.post("/rag/query", response_model=RAGQueryResponse, summary="Query documents using RAG")
def rag_query(request: RAGQueryRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query string is required.")
    result = rag_service.query_document(user_id=current_user["id"], query=request.query)
    return RAGQueryResponse(**result)

@router.post("/rag/reindex", summary="Reindex all documents in the RAG DB")
def reindex_all_documents(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("is_admin") is not True:
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    rag_service.reindex_all_documents(db)
    return {"detail": "Reindexing started."}
