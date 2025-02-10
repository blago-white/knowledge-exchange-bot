from .common import router as COMMON_ROUTER
from .workers import router as WORKER_ROUTER
from .lessons import router as LESSONS_ROUTER
from .sales import (router as SALES_ROUTER)


__all__ = ["ROUTERS"]

print(globals().keys())

ROUTERS = [val for name, val in globals().items() if name[0].isupper()]
