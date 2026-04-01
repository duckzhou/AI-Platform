"""
大模型对话服务
"""
import uuid
import json
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.chat_history import ChatHistory, ChatRole
from app.models.ai_model import AIModel
from app.services.dashscope_service import DashScopeService, THINK_START, THINK_END


class ChatService:
    """对话服务"""
    
    @staticmethod
    async def get_chat_models(db: AsyncSession) -> List[Dict[str, Any]]:
        """获取可用的对话模型"""
        # 返回通义千问模型列表
        return DashScopeService.get_model_list()
    
    @staticmethod
    async def get_chat_history(db: AsyncSession, user_id: int, session_id: str = None,
                                limit: int = 50) -> List[ChatHistory]:
        """获取对话历史"""
        query = select(ChatHistory).where(
            ChatHistory.user_id == user_id,
            ChatHistory.is_deleted == False
        )
        
        if session_id:
            query = query.where(ChatHistory.session_id == session_id)
        
        query = query.order_by(desc(ChatHistory.created_at)).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_sessions(db: AsyncSession, user_id: int, page: int = 1, size: int = 20):
        """获取用户的会话列表"""
        from sqlalchemy import distinct
        
        # 获取会话列表
        result = await db.execute(
            select(
                ChatHistory.session_id,
                func.max(ChatHistory.session_name).label("session_name"),
                func.max(ChatHistory.created_at).label("last_time"),
                func.count(ChatHistory.id).label("message_count")
            )
            .where(ChatHistory.user_id == user_id, ChatHistory.is_deleted == False)
            .group_by(ChatHistory.session_id)
            .order_by(desc("last_time"))
            .offset((page - 1) * size)
            .limit(size)
        )
        
        sessions = []
        for row in result.all():
            sessions.append({
                "session_id": row.session_id,
                "session_name": row.session_name or "新对话",
                "last_time": row.last_time.isoformat() if row.last_time else None,
                "message_count": row.message_count
            })
        
        return sessions
    
    @staticmethod
    async def create_session(user_id: int, session_name: str = None) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        return session_id
    
    @staticmethod
    async def save_message(db: AsyncSession, user_id: int, session_id: str,
                           role: ChatRole, content: str, model_code: str = None,
                           meta_info: dict = None) -> ChatHistory:
        """保存消息"""
        message = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            model_code=model_code,
            meta_info=meta_info
        )
        db.add(message)
        await db.commit()
        return message
    
    @staticmethod
    async def update_session_name(db: AsyncSession, user_id: int, session_id: str, name: str):
        """更新会话名称"""
        from sqlalchemy import update
        await db.execute(
            update(ChatHistory)
            .where(
                ChatHistory.user_id == user_id,
                ChatHistory.session_id == session_id
            )
            .values(session_name=name)
        )
        await db.commit()
    
    @staticmethod
    async def delete_session(db: AsyncSession, user_id: int, session_id: str):
        """删除会话"""
        from sqlalchemy import update
        await db.execute(
            update(ChatHistory)
            .where(
                ChatHistory.user_id == user_id,
                ChatHistory.session_id == session_id
            )
            .values(is_deleted=True)
        )
        await db.commit()
    
    @staticmethod
    async def chat_stream(db: AsyncSession, user_id: int, session_id: str, message: str,
                          model_code: str = "qwen-turbo", is_deep_think: bool = False,
                          is_web_search: bool = False) -> AsyncGenerator[str, None]:
        """
        流式对话
        支持打字机效果
        """
        import logging
        logger = logging.getLogger(__name__)
            
        # 获取历史消息
        history = await ChatService.get_chat_history(db, user_id, session_id, limit=10)
        messages = []
            
        # 添加系统提示
        system_prompt = "你是一个 helpful AI 助手。"
        if is_deep_think and DashScopeService.supports_deep_think(model_code):
            system_prompt += "请深度思考后再回答。"
        messages.append({"role": "system", "content": system_prompt})
            
        # 添加历史消息
        for h in reversed(history):
            messages.append({"role": h.role.value, "content": h.content})
            
        # 添加用户消息
        messages.append({"role": "user", "content": message})
            
        logger.info(f"开始流式对话，模型：{model_code}, 消息数：{len(messages)}")
            
        # 保存用户消息
        await ChatService.save_message(
            db, user_id, session_id, ChatRole.USER, message, model_code,
            {"is_deep_think": is_deep_think, "is_web_search": is_web_search}
        )
            
        # 调用 DashScope 流式 API
        response_content = ""
        reasoning_content = ""
        try:
            logger.info("开始调用 DashScope 流式 API")
            chunk_count = 0
            async for chunk in DashScopeService.chat_stream(
                messages=messages,
                model=model_code,
                is_deep_think=is_deep_think,
                is_web_search=is_web_search
            ):
                chunk_count += 1
                logger.debug(f"收到 chunk #{chunk_count}: {repr(chunk[:200])}")
                yield chunk
                
                # 累积内容用于保存
                if chunk.startswith("data:"):
                    data_str = chunk[5:].strip()
                    try:
                        data = json.loads(data_str)
                        logger.debug(f"解析后的数据：{data}")
                        if "content" in data:
                            response_content += data["content"]
                            logger.debug(f"累积 content: {len(response_content)} chars")
                        if "reasoning_content" in data:
                            reasoning_content += data["reasoning_content"]
                            logger.debug(f"累积 reasoning_content: {len(reasoning_content)} chars")
                        elif data.get("done"):
                            logger.info(f"对话结束，总 content 长度：{len(response_content)}, reasoning 长度：{len(reasoning_content)}")
                            # 保存 AI 回复（包含思考过程）
                            full_content = response_content
                            if reasoning_content:
                                full_content = THINK_START + reasoning_content + THINK_END + response_content
                            
                            await ChatService.save_message(
                                db, user_id, session_id, ChatRole.ASSISTANT, full_content, model_code
                            )
                            logger.info("已保存 AI 回复")
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON 解析失败：{e}, 原始数据：{data_str}")
            logger.info(f"流式对话完成，总共收到 {chunk_count} 个 chunk")
        except Exception as e:
            logger.error(f"流式对话出错：{e}", exc_info=True)
            error_msg = f"调用模型失败：{str(e)}"
            yield f"data: {json.dumps({'content': error_msg})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    @staticmethod
    async def chat(db: AsyncSession, user_id: int, session_id: str, message: str,
                   model_code: str = "qwen-turbo", is_deep_think: bool = False,
                   is_web_search: bool = False) -> str:
        """非流式对话"""
        # 保存用户消息
        await ChatService.save_message(
            db, user_id, session_id, ChatRole.USER, message, model_code,
            {"is_deep_think": is_deep_think, "is_web_search": is_web_search}
        )
        
        # 获取历史消息
        history = await ChatService.get_chat_history(db, user_id, session_id, limit=10)
        messages = []
        
        # 添加系统提示
        system_prompt = "你是一个 helpful AI 助手。"
        if is_deep_think and DashScopeService.supports_deep_think(model_code):
            system_prompt += "请深度思考后再回答。"
        messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史消息
        for h in reversed(history):
            messages.append({"role": h.role.value, "content": h.content})
        
        # 添加用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用 DashScope API
        try:
            response = await DashScopeService.chat(
                messages=messages,
                model=model_code,
                is_deep_think=is_deep_think,
                is_web_search=is_web_search
            )
        except Exception as e:
            response = f"调用模型失败：{str(e)}"
        
        # 保存AI回复
        await ChatService.save_message(
            db, user_id, session_id, ChatRole.ASSISTANT, response, model_code
        )
        
        return response
