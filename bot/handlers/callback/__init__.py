from .workers import router as WORKERS_INLINE_ROUTER
from .lessons import router as LESSONS_INLINE_ROUTER
from .sales import router as SALES_INLINE_ROUTER

__all__ = ["LESSONS_INLINE_ROUTER", "WORKERS_INLINE_ROUTER"]

ROUTERS = [val for name, val in globals().items() if name[0].isupper()]
