import time
import logging
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO)
file_logger = logging.getLogger("lopdp_logger")
fh = logging.FileHandler("logs/api_requests.log", encoding="utf-8")
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
file_logger.addHandler(fh)

class LoggingLOPDPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duracion_ms = round((time.time() - start_time) * 1000, 2)

        log_line = (
            f"METHOD={request.method} PATH={request.url.path} "
            f"STATUS={response.status_code} DURATION={duracion_ms}ms"
        )
        file_logger.info(log_line)
        print(f"[AUDIT LOPDP] {log_line}")
        return response
