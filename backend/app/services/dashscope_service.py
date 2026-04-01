"""
DashScope (通义千问) 服务
"""
import json
from typing import List, Dict, Any, AsyncGenerator
import dashscope
from dashscope import Generation

from app.core.config import settings

# 配置 DashScope API Key
dashscope.api_key = settings.DASHSCOPE_API_KEY

# 思考标签常量
THINK_START = "<think>\n"
THINK_END = "\n</think>\n\n"


class DashScopeService:
    """通义千问服务"""
    
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    
    # 通义千问模型配置
    MODELS = {
        "qwen-turbo": {
            "name": "通义千问 Turbo",
            "supports_deep_think": False,
            "supports_web_search": False,
            "quota_cost": 1,
        },
        "qwen-plus": {
            "name": "通义千问 Plus",
            "supports_deep_think": True,
            "supports_web_search": True,
            "quota_cost": 2,
        },
        "qwen-max": {
            "name": "通义千问 Max",
            "supports_deep_think": True,
            "supports_web_search": True,
            "quota_cost": 4,
        },
        "qwen-coder-plus": {
            "name": "通义千问 Coder",
            "supports_deep_think": False,
            "supports_web_search": False,
            "quota_cost": 2,
        },
        "qwen-vl-plus": {
            "name": "通义千问 VL (视觉)",
            "supports_deep_think": False,
            "supports_web_search": False,
            "quota_cost": 3,
        },
    }
    
    @staticmethod
    def get_model_list() -> List[Dict[str, Any]]:
        """获取模型列表"""
        return [
            {
                "code": code,
                "name": config["name"],
                "supports_deep_think": config["supports_deep_think"],
                "supports_web_search": config["supports_web_search"],
                "quota_cost": config["quota_cost"],
            }
            for code, config in DashScopeService.MODELS.items()
        ]
    
    @staticmethod
    def supports_deep_think(model_code: str) -> bool:
        """是否支持深度思考"""
        return DashScopeService.MODELS.get(model_code, {}).get("supports_deep_think", False)
    
    @staticmethod
    def supports_web_search(model_code: str) -> bool:
        """是否支持联网搜索"""
        return DashScopeService.MODELS.get(model_code, {}).get("supports_web_search", False)
    
    @staticmethod
    def _safe_get(obj, *attrs, default=None):
        """安全地获取嵌套属性"""
        for attr in attrs:
            try:
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    obj = obj.get(attr)
                else:
                    obj = getattr(obj, attr, None)
            except Exception:
                return default
        return obj if obj is not None else default
    
    @staticmethod
    async def chat(
        messages: List[Dict[str, str]],
        model: str = "qwen-turbo",
        is_deep_think: bool = False,
        is_web_search: bool = False,
    ) -> str:
        """非流式对话 - 使用 DashScope SDK"""
        params = {
            "model": model,
            "messages": messages,
            "result_format": "message",
        }
        
        if is_deep_think and DashScopeService.supports_deep_think(model):
            params["enable_thinking"] = True
            params["thinking_budget"] = 8192
        
        if is_web_search and DashScopeService.supports_web_search(model):
            params["enable_search"] = True
        
        response = Generation.call(**params)
        
        if response.status_code == 200:
            content = DashScopeService._safe_get(response, 'output', 'choices', 0, 'message', 'content') or ""
            
            # 安全地获取 reasoning_content
            reasoning_content = DashScopeService._safe_get(
                response, 'output', 'choices', 0, 'message', 'reasoning_content'
            )
            if reasoning_content:
                content = THINK_START + reasoning_content + THINK_END + content
            
            return content
        else:
            raise Exception(f"API调用失败: {response.message}")
    
    @staticmethod
    async def chat_stream(
        messages: List[Dict[str, str]],
        model: str = "qwen-turbo",
        is_deep_think: bool = False,
        is_web_search: bool = False,
    ) -> AsyncGenerator[str, None]:
        """流式对话 (SSE) - 使用 DashScope SDK"""
        import logging
        logger = logging.getLogger(__name__)
            
        params = {
            "model": model,
            "messages": messages,
            "result_format": "message",
            "stream": True,
            "incremental_output": True,  # 关键！返回增量内容而非累积内容
        }
            
        if is_deep_think and DashScopeService.supports_deep_think(model):
            params["enable_thinking"] = True
            params["thinking_budget"] = 8192
            
        if is_web_search and DashScopeService.supports_web_search(model):
            params["enable_search"] = True
            
        try:
            # 使用生成器模式进行流式调用
            logger.info(f"DashScope SDK 调用参数：model={model}, stream=True")
            responses = Generation.call(**params)
                    
            # 检查是否是生成器对象
            if hasattr(responses, '__iter__'):
                logger.info("SDK 返回了生成器对象，开始迭代")
                response_count = 0
                last_content = ""  # 记录上次的内容
                last_reasoning = ""  # 记录上次的 reasoning
                        
                for response in responses:
                    response_count += 1
                    logger.debug(f"收到 SDK 响应 #{response_count}: status={response.status_code}")
                                    
                    if response.status_code == 200:
                        # 直接从 output.choices[0].message 获取内容
                        try:
                            output = response.output
                            if output and hasattr(output, 'choices') and output.choices:
                                choice = output.choices[0]
                                if hasattr(choice, 'message'):
                                    # Message 对象可能是 dict 或对象
                                    if isinstance(choice.message, dict):
                                        content = choice.message.get('content')
                                        reasoning_content = choice.message.get('reasoning_content')
                                    else:
                                        # 尝试作为对象访问
                                        content = getattr(choice.message, 'content', None)
                                        reasoning_content = getattr(choice.message, 'reasoning_content', None)
                                                        
                                    logger.debug(f"直接提取得到：content={repr(content)}, reasoning={repr(reasoning_content)}")
                                else:
                                    logger.warning("choice 没有 message 属性")
                                    content = None
                                    reasoning_content = None
                            else:
                                logger.warning("output 没有 choices 或 choices 为空")
                                content = None
                                reasoning_content = None
                        except Exception as e:
                            logger.error(f"提取内容失败：{e}", exc_info=True)
                            content = None
                            reasoning_content = None
                                            
                        # 处理 incremental_output
                        if content or reasoning_content:
                            logger.info(f"提取到内容：content={len(content) if content else 0} chars, reasoning={len(reasoning_content) if reasoning_content else 0} chars")
                            data = {}
                            if reasoning_content:
                                data['reasoning_content'] = reasoning_content
                            if content:
                                data['content'] = content
                                    
                            if data:
                                chunk = f"data: {json.dumps(data)}\n\n"
                                logger.debug(f"yield chunk: {repr(chunk[:100])}")
                                yield chunk
                    else:
                        error_msg = f'错误：{response.message}'
                        logger.error(error_msg)
                        yield f"data: {json.dumps({'content': error_msg})}\n\n"
                
                logger.info(f"SDK 生成器迭代完成，共收到 {response_count} 个响应")
            else:
                # 如果不是生成器，可能是配置问题
                logger.error(f"Generation.call() 没有返回生成器对象，返回类型：{type(responses)}")
                yield f"data: {json.dumps({'content': '流式调用失败：SDK 未返回生成器'})}\n\n"
        except Exception as e:
            logger.error(f"流式调用异常：{e}", exc_info=True)
            yield f"data: {json.dumps({'content': f'流式调用失败：{str(e)}'})}\n\n"
            
        yield f"data: {json.dumps({'done': True})}\n\n"
