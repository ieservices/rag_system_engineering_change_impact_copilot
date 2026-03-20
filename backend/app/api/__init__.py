from fastapi import APIRouter
from .chat import router as chat_router
from .search import router as search_router
from .parts import router as parts_router
from .assemblies import router as assemblies_router
from .documents import router as documents_router
from .change_requests import router as cr_router
from .admin import router as admin_router
from .sessions import router as sessions_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(parts_router, prefix="/parts", tags=["Parts"])
api_router.include_router(assemblies_router, prefix="/assemblies", tags=["Assemblies"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(cr_router, prefix="/change-requests", tags=["Change Requests"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
