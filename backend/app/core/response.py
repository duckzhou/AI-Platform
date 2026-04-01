"""
统一响应格式
"""
from typing import Any, Optional, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class ResponseCode:
    """响应状态码"""
    SUCCESS = 200
    ERROR = 500
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    VALIDATION_ERROR = 422
    QUOTA_EXCEEDED = 1001
    TASK_FAILED = 1002


def success(data: Any = None, message: str = "success") -> ResponseModel:
    """成功响应"""
    return ResponseModel(code=ResponseCode.SUCCESS, message=message, data=data)


def error(message: str = "error", code: int = ResponseCode.ERROR, data: Any = None) -> ResponseModel:
    """错误响应"""
    return ResponseModel(code=code, message=message, data=data)


def json_response(result: ResponseModel) -> JSONResponse:
    """JSON响应"""
    return JSONResponse(
        status_code=200 if result.code == ResponseCode.SUCCESS else 400,
        content=result.model_dump()
    )
