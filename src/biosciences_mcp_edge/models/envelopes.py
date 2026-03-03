"""Canonical envelope models per ADR-001 Section 8.

Local copy — no cross-repo import dependency on biosciences-mcp.
"""

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorCode(StrEnum):
    """Standard error codes from ADR-001 Appendix B."""

    UNRESOLVED_ENTITY = "UNRESOLVED_ENTITY"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"


class ErrorDetail(BaseModel):
    """Error detail object within ErrorEnvelope."""

    code: ErrorCode = Field(description="Error code from registry")
    message: str = Field(description="Human-readable error message")
    recovery_hint: str = Field(description="Agent-actionable guidance for recovery")
    invalid_input: str | None = Field(default=None, description="The input that caused the error")


class ErrorEnvelope(BaseModel):
    """Canonical error envelope per ADR-001 Section 8."""

    success: bool = Field(default=False, description="Always false for errors")
    error: ErrorDetail = Field(description="Error details with recovery hint")

    @classmethod
    def unresolved_entity(cls, invalid_input: str) -> "ErrorEnvelope":
        return cls(
            error=ErrorDetail(
                code=ErrorCode.UNRESOLVED_ENTITY,
                message=f"The input '{invalid_input}' is not a valid identifier.",
                recovery_hint="Use a search tool to resolve the identifier first.",
                invalid_input=invalid_input,
            )
        )

    @classmethod
    def entity_not_found(cls, entity_id: str) -> "ErrorEnvelope":
        return cls(
            error=ErrorDetail(
                code=ErrorCode.ENTITY_NOT_FOUND,
                message=f"No results found for '{entity_id}'.",
                recovery_hint="Verify the identifier or try a different query.",
                invalid_input=entity_id,
            )
        )

    @classmethod
    def rate_limited(cls, retry_after: int | None = None) -> "ErrorEnvelope":
        hint = "Retry after a few seconds."
        if retry_after:
            hint = f"Retry after {retry_after} seconds."
        return cls(
            error=ErrorDetail(
                code=ErrorCode.RATE_LIMITED,
                message="API rate limit exceeded.",
                recovery_hint=hint,
            )
        )

    @classmethod
    def upstream_error(cls, status_code: int, detail: str | None = None) -> "ErrorEnvelope":
        message = f"Upstream API returned error {status_code}."
        if detail:
            message = f"{message} {detail}"
        return cls(
            error=ErrorDetail(
                code=ErrorCode.UPSTREAM_ERROR,
                message=message,
                recovery_hint="The upstream API may be temporarily unavailable. Retry later.",
            )
        )


class Pagination(BaseModel):
    """Pagination metadata within PaginationEnvelope."""

    cursor: str | None = Field(default=None, description="Opaque cursor for next page; null = end")
    total_count: int | None = Field(default=None, description="Total items if known")
    page_size: int = Field(default=50, description="Items per page")


class PaginationEnvelope(BaseModel, Generic[T]):
    """Canonical pagination envelope per ADR-001 Section 8."""

    items: list[T] = Field(description="Data payload")
    pagination: Pagination = Field(description="Pagination metadata")

    @classmethod
    def create(
        cls,
        items: list[T],
        cursor: str | None = None,
        total_count: int | None = None,
        page_size: int = 50,
    ) -> "PaginationEnvelope[T]":
        return cls(
            items=items,
            pagination=Pagination(
                cursor=cursor,
                total_count=total_count,
                page_size=page_size,
            ),
        )
