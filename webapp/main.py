from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.api import book_router
from webapp.logger import LogServerMiddleware
from webapp.metrics import MeasureLatencyMiddleware, metrics


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(MeasureLatencyMiddleware)
    app.add_middleware(LogServerMiddleware)

    # CORS Middleware should be the last.
    # See https://github.com/tiangolo/fastapi/issues/1663 .
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # CORS разрешено для всех доменов.
        allow_credentials=True,  # Разрешает использование cookie в cross-origin запросах
        allow_methods=["*"],  # Разрешает все HTTP методы
        allow_headers=["*"],
    )


def setup_routers(app: FastAPI) -> None:
    app.add_route("/metrics", metrics)

    app.include_router(book_router)


def create_app() -> FastAPI:
    app = FastAPI()

    setup_middleware(app)
    setup_routers(app)

    return app
