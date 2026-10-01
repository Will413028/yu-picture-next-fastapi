from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.database import build_engine, check_database
from app.users import router as user_router


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    database: Literal["connected", "disconnected"]


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        engine = build_engine()
        application.state.engine = engine
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(title="Yu Picture API", version="0.1.0", lifespan=lifespan)
    application.include_router(user_router)

    @application.exception_handler(RequestValidationError)
    def invalid_input(request: Request, error: RequestValidationError):
        # Pydantic errors can contain supplied passwords or codes in their input field.
        return JSONResponse({"detail": "輸入格式不正確，請檢查欄位"}, status_code=422)

    @application.exception_handler(SQLAlchemyError)
    def database_failure(request: Request, error: SQLAlchemyError):
        return JSONResponse({"detail": "服務暫時無法使用"}, status_code=503)

    @application.get("/api/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @application.get(
        "/api/v1/ready",
        response_model=ReadinessResponse,
        responses={503: {"model": ReadinessResponse}},
    )
    def ready(request: Request, response: Response) -> ReadinessResponse:
        response.headers["Cache-Control"] = "no-store"
        try:
            check_database(request.app.state.engine)
        except SQLAlchemyError:
            response.status_code = 503
            return ReadinessResponse(status="unavailable", database="disconnected")
        return ReadinessResponse(status="ready", database="connected")

    return application


app = create_app()
