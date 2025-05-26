from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sentry_sdk import capture_exception


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        capture_exception(exc)

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": exc.errors()}),
        )


def sentry_exception_middleware(app):
    @app.middleware("http")
    async def sentry_exception_middleware(request: Request, call_next):
        try:
            response = await call_next(request)

            return response
        
        except HTTPException as http_exc:
            capture_exception(http_exc)

            raise http_exc
        
        except Exception as exc:
            capture_exception(exc)

            return JSONResponse(
                status_code=500,
                content={"detail": f"Erro interno do servidor: {exc}"},
            )
        