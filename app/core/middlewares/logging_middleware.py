import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logging.info(f"📥 {method} {url} - IP: {client_host} - UA: {user_agent}")

        # Ejecutar la siguiente capa del middleware
        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        # Colores para códigos HTTP
        status_color = (
            "\033[92m" if 200 <= status_code < 300 else  # Verde
            "\033[93m" if 300 <= status_code < 400 else  # Amarillo
            "\033[91m"                                   # Rojo
        )

        logging.info(
            f"📤 {status_color}{status_code}\033[0m "
            f"({process_time:.2f} ms)"
        )

        return response
