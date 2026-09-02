from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Consistent, user-safe error shape. Never includes stack traces or internals."""

    error: str = Field(..., description="Short machine-readable error code.")
    message: str
    detail: str | None = None
