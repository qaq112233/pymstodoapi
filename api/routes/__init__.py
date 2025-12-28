"""
API Routes Package
"""
from .auth import router as auth_router
from .lists import router as lists_router
from .tasks import router as tasks_router, lists_tasks_router
from .html import router as html_router

# Merge tasks router with lists router for /lists/{id}/tasks endpoints
lists_router.include_router(lists_tasks_router, prefix="", tags=["Tasks"])

__all__ = ["auth_router", "lists_router", "tasks_router", "html_router"]
