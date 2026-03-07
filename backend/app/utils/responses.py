"""
Standard API response helpers — keeps all responses consistent:
{ success: bool, data: any, message: str, pagination?: {} }
"""
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    pagination: Optional[Dict] = None,
) -> JSONResponse:
    body: Dict[str, Any] = {"success": True, "message": message, "data": data}
    if pagination:
        body["pagination"] = pagination
    return JSONResponse(content=body, status_code=status_code)


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[Any] = None,
) -> JSONResponse:
    body: Dict[str, Any] = {"success": False, "message": message, "data": None}
    if errors:
        body["errors"] = errors
    return JSONResponse(content=body, status_code=status_code)


def paginate(items: list, total: int, page: int, limit: int) -> Dict:
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": max(1, -(-total // limit)),  # ceil division
        "has_next": (page * limit) < total,
        "has_prev": page > 1,
    }
