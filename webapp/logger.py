import logging
import uuid
from contextvars import ContextVar

import yaml
from starlette.types import ASGIApp, Receive, Scope, Send

with open("conf/logging.conf.yml", "r") as f:
    LOGGING_CONFIG = yaml.full_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        try:
            correlation_id = correlation_id_ctx.get()
            return "[%s] %s" % (correlation_id, super().format(record))
        except LookupError:
            return super().format(record)


correlation_id_ctx = ContextVar("correlation_id_ctx")
logger = logging.getLogger("mem_bot")


class LogServerMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        for header, value in scope["headers"]:
            if header == b"x-correlation-id":
                correlation_id_ctx.set(value.decode())
                break
        else:
            correlation_id_ctx.set(uuid.uuid4().hex)

        await self.app(scope, receive, send)
