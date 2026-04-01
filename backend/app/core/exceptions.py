"""
全局异常处理
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.response import error, ResponseCode, ResponseModel

logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str = "业务错误", code: int = ResponseCode.ERROR):
        self.message = message
        self.code = code
        super().__init__(self.message)


class QuotaException(BusinessException):
    """额度异常"""
    def __init__(self, message: str = "额度不足"):
        super().__init__(message=message, code=ResponseCode.QUOTA_EXCEEDED)


class AuthException(BusinessException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message=message, code=ResponseCode.UNAUTHORIZED)


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    logger.warning(f"Business exception: {exc.message}, Code: {exc.code}")
    return JSONResponse(
        status_code=200,
        content=error(message=exc.message, code=exc.code).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证异常处理"""
    errors = exc.errors()
    message = errors[0].get("msg", "参数验证失败") if errors else "参数验证失败"
    logger.warning(f"Validation error: {message}")
    return JSONResponse(
        status_code=200,
        content=error(message=message, code=ResponseCode.VALIDATION_ERROR).model_dump()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=200,
        content=error(message="数据库操作失败", code=ResponseCode.ERROR).model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=error(message="服务器内部错误", code=ResponseCode.ERROR).model_dump()
    )


def register_exception_handlers(app):
    """注册异常处理器"""
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(QuotaException, business_exception_handler)
    app.add_exception_handler(AuthException, business_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
