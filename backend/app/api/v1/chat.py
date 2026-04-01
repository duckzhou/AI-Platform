"""
对话相关API
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json

from app.api.deps import DBDep, CurrentUser
from app.core.response import success
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: str = None
    message: str
    model_code: str = "gpt-3.5-turbo"
    is_deep_think: bool = False
    is_web_search: bool = False


class RenameSessionRequest(BaseModel):
    """重命名会话请求"""
    name: str


@router.get("/models")
async def get_models(db: AsyncSession = DBDep):
    """获取可用模型列表"""
    models = await ChatService.get_chat_models(db)
    return success(models)


@router.get("/sessions")
async def get_sessions(
    page: int = 1,
    size: int = 20,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """获取会话列表"""
    sessions = await ChatService.get_user_sessions(db, user_id, page, size)
    return success({"list": sessions})


@router.post("/sessions")
async def create_session(user_id: int = CurrentUser):
    """创建新会话"""
    session_id = await ChatService.create_session(user_id)
    return success({"session_id": session_id})


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    limit: int = 50,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """获取会话消息历史"""
    messages = await ChatService.get_chat_history(db, user_id, session_id, limit)
    return success({
        "list": [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "model_code": m.model_code,
                "meta_info": m.meta_info,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    })


@router.post("/send")
async def send_message(req: ChatRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """发送消息（非流式）"""
    if not req.session_id:
        req.session_id = await ChatService.create_session(user_id)
    
    response = await ChatService.chat(
        db, user_id, req.session_id, req.message,
        req.model_code, req.is_deep_think, req.is_web_search
    )
    
    return success({
        "session_id": req.session_id,
        "response": response
    })


@router.post("/send-stream")
async def send_message_stream(req: ChatRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """发送消息（流式/SSE）"""
    if not req.session_id:
        req.session_id = await ChatService.create_session(user_id)
    
    async def event_generator():
        async for chunk in ChatService.chat_stream(
            db, user_id, req.session_id, req.message,
            req.model_code, req.is_deep_think, req.is_web_search
        ):
            yield chunk
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.put("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    req: RenameSessionRequest,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """重命名会话"""
    await ChatService.update_session_name(db, user_id, session_id, req.name)
    return success(None, "重命名成功")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """删除会话"""
    await ChatService.delete_session(db, user_id, session_id)
    return success(None, "删除成功")
