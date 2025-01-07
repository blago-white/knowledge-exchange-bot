from .workers import router as WORKERS_INLINE_ROUTER

__all__ = ["WORKERS_INLINE_ROUTER"]

print(globals().keys())

ROUTERS = [val for name, val in globals().items() if name[0].isupper()]
