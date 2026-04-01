"""
阿里云百炼 AI 服务
- 文生图/图生图: qwen-image-2.0-pro (同步)
- 图生视频: wan2.6-i2v-flash (异步轮询)
"""
import httpx
from typing import List, Optional
import uuid
import logging

from app.core.config import settings
from app.services.oss_service import OSSService

logger = logging.getLogger(__name__)

# API 地址
QWEN_IMAGE_API = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
VIDEO_API = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
TASK_QUERY_API = "https://dashscope.aliyuncs.com/api/v1/tasks"


class QwenImageService:
    """千问图像生成服务 - 同步接口"""
    
    # 图片尺寸映射
    SIZES = {
        "1024x1024": "1024*1024",
        "720x1280": "720*1280",
        "1280x720": "1280*720",
        "768x1152": "768*1152",
        "1536x1536": "1536*1536",
    }
    
    MODEL = "qwen-image-2.0-pro"
    
    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }
    
    @staticmethod
    def text_to_image(
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        negative_prompt: str = "低分辨率，低画质，肢体畸形，手指畸形",
    ) -> List[str]:
        """文生图（同步）"""
        logger.info(f"[文生图] 开始: prompt={prompt[:50]}..., size={size}")
        
        payload = {
            "model": QwenImageService.MODEL,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [{"text": prompt}]
                }]
            },
            "parameters": {
                "size": QwenImageService.SIZES.get(size, "1024*1024"),
                "n": n,
                "negative_prompt": negative_prompt,
                "prompt_extend": True,
                "watermark": False
            }
        }
        
        with httpx.Client(timeout=120) as client:
            response = client.post(QWEN_IMAGE_API, headers=QwenImageService._get_headers(), json=payload)
            result = response.json()
        
        logger.info(f"[文生图] API状态码: {response.status_code}")
        
        if response.status_code != 200 or "output" not in result:
            error_msg = result.get("message", result.get("error", str(result)))
            logger.error(f"[文生图] 失败: {error_msg}")
            raise Exception(f"生成失败: {error_msg}")
        
        return QwenImageService._extract_image_urls(result["output"], "文生图")
    
    @staticmethod
    def image_to_image(
        prompt: str,
        image_url: str,
        size: str = "1024x1024",
        n: int = 1,
    ) -> List[str]:
        """图生图（同步）"""
        logger.info(f"[图生图] 开始: prompt={prompt[:50]}...")
        
        payload = {
            "model": QwenImageService.MODEL,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"image": image_url},
                        {"text": prompt}
                    ]
                }]
            },
            "parameters": {
                "size": QwenImageService.SIZES.get(size, "1024*1024"),
                "n": n,
                "prompt_extend": True,
                "watermark": False
            }
        }
        
        with httpx.Client(timeout=120) as client:
            response = client.post(QWEN_IMAGE_API, headers=QwenImageService._get_headers(), json=payload)
            result = response.json()
        
        logger.info(f"[图生图] API状态码: {response.status_code}")
        
        if response.status_code != 200 or "output" not in result:
            error_msg = result.get("message", result.get("error", str(result)))
            logger.error(f"[图生图] 失败: {error_msg}")
            raise Exception(f"生成失败: {error_msg}")
        
        return QwenImageService._extract_image_urls(result["output"], "图生图")
    
    @staticmethod
    def _extract_image_urls(output: dict, task_type: str) -> List[str]:
        """从 API 响应中提取图片 URL"""
        image_urls = []
        
        # 新格式: choices[].message.content[].image
        if "choices" in output:
            for choice in output["choices"]:
                content = choice.get("message", {}).get("content", [])
                for item in content:
                    if "image" in item:
                        image_urls.append(item["image"])
        # 旧格式: results[].url
        elif "results" in output:
            image_urls = [r["url"] for r in output["results"] if "url" in r]
        
        logger.info(f"[{task_type}] 成功: 提取到 {len(image_urls)} 张图片")
        return image_urls
    
    @staticmethod
    async def save_results(image_urls: List[str]) -> List[dict]:
        """下载图片并保存到 OSS"""
        logger.info(f"[OSS] 开始保存 {len(image_urls)} 张图片")
        results = []
        for url in image_urls:
            save_url = await QwenImageService._download_and_upload(url)
            results.append({"url": url, "save_url": save_url})
        logger.info(f"[OSS] 保存完成")
        return results
    
    @staticmethod
    async def _download_and_upload(url: str) -> str:
        """下载并上传到 OSS"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60)
            response.raise_for_status()
            content = response.content
        
        filename = f"{uuid.uuid4().hex}.png"
        result = OSSService.upload_file(content, filename, folder="generated")
        return result["file_url"]


class VideoService:
    """视频生成服务 - 异步轮询"""
    
    MODEL = "wan2.6-i2v-flash"  # 快速版
    
    @staticmethod
    def _get_headers(async_mode: bool = False):
        headers = {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }
        if async_mode:
            headers["X-DashScope-Async"] = "enable"
        return headers
    
    @staticmethod
    def submit_image_to_video(
        image_url: str,
        prompt: str = "",
        duration: int = 5,
        resolution: str = "720P",
    ) -> str:
        """提交图生视频任务，返回 task_id"""
        logger.info(f"[图生视频] 提交任务: image_url={image_url[:60]}...")
        
        payload = {
            "model": VideoService.MODEL,
            "input": {
                "img_url": image_url,
            },
            "parameters": {
                "resolution": resolution,
                "duration": duration,
                "prompt_extend": True,
            }
        }
        
        # 添加 prompt（可选）
        if prompt:
            payload["input"]["prompt"] = prompt
        
        with httpx.Client(timeout=30) as client:
            response = client.post(VIDEO_API, headers=VideoService._get_headers(async_mode=True), json=payload)
            result = response.json()
        
        logger.info(f"[图生视频] 提交响应: {result}")
        
        # 提取 task_id
        task_id = result.get("output", {}).get("task_id")
        if not task_id:
            error_msg = result.get("message", str(result))
            logger.error(f"[图生视频] 提交失败: {error_msg}")
            raise Exception(f"提交失败: {error_msg}")
        
        logger.info(f"[图生视频] 任务已提交: task_id={task_id}")
        return task_id
    
    @staticmethod
    def check_video_task(task_id: str) -> dict:
        """查询视频任务状态"""
        url = f"{TASK_QUERY_API}/{task_id}"
        
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers={
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}"
            })
            result = response.json()
        
        output = result.get("output", {})
        status = output.get("task_status", "UNKNOWN")
        
        logger.info(f"[图生视频] 任务状态: task_id={task_id}, status={status}")
        
        if status == "SUCCEEDED":
            # 提取视频 URL
            video_url = output.get("video_url") or output.get("results", [{}])[0].get("url")
            if video_url:
                logger.info(f"[图生视频] 任务成功: video_url={video_url[:60]}...")
                return {"status": "SUCCEEDED", "video_url": video_url}
            else:
                logger.error(f"[图生视频] 未找到视频URL: {output}")
                return {"status": "FAILED", "error": "未找到视频URL"}
        
        elif status == "FAILED":
            error = output.get("message", "任务失败")
            logger.error(f"[图生视频] 任务失败: {error}")
            return {"status": "FAILED", "error": error}
        
        else:
            # PENDING / RUNNING
            return {"status": status}
    
    @staticmethod
    async def download_and_upload_video(video_url: str) -> str:
        """下载视频并上传到 OSS"""
        logger.info(f"[OSS] 开始下载视频: {video_url[:60]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=120)
            response.raise_for_status()
            content = response.content
        
        filename = f"{uuid.uuid4().hex}.mp4"
        result = OSSService.upload_file(content, filename, folder="videos")
        logger.info(f"[OSS] 视频保存成功: {result['file_url'][:60]}...")
        return result["file_url"]


# 兼容旧代码的别名
WanxService = QwenImageService
