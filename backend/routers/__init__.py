from .health_routers import router as health_router
from .auth_routers import router as auth_router

__all__ = ["health_router", "auth_router"]
