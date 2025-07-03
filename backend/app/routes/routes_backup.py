from fastapi import APIRouter
from .auth import router as auth_router
from .document import router as documents_router
from .query import router as query_router

auth = auth_router
documents = documents_router
query = query_router

__all__ = ["auth", "documents", "query"]