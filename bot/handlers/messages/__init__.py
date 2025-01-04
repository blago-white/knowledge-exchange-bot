from .common import router as COMMON_ROUTER

__all__ = ["ROUTERS"]

print(globals().keys())

ROUTERS = [val for name, val in globals().items() if name[0].isupper()]
