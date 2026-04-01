"""
阿里云 OSS 服务
"""
import oss2
from datetime import datetime
import uuid
from typing import Optional

from app.core.config import settings


class OSSService:
    """阿里云 OSS 服务"""
    
    _bucket = None
    
    @classmethod
    def get_bucket(cls):
        """获取 OSS Bucket 实例"""
        if cls._bucket is None:
            auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
            cls._bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
        return cls._bucket
    
    @classmethod
    def upload_file(cls, file_content: bytes, filename: str, folder: str = "materials") -> dict:
        """
        上传文件到 OSS
        
        Args:
            file_content: 文件内容
            filename: 原始文件名
            folder: 存储目录
            
        Returns:
            dict: 包含 file_url 和 file_key
        """
        bucket = cls.get_bucket()
        
        # 生成唯一文件名
        file_ext = filename.split(".")[-1].lower() if "." in filename else ""
        date_dir = datetime.now().strftime("%Y/%m/%d")
        unique_name = f"{uuid.uuid4().hex}.{file_ext}"
        
        # OSS 存储路径
        file_key = f"{folder}/{date_dir}/{unique_name}"
        
        # 根据扩展名设置 Content-Type
        content_type = cls._get_content_type(file_ext)
        headers = {'Content-Type': content_type} if content_type else {}
        
        # 上传文件
        bucket.put_object(file_key, file_content, headers=headers)
        
        # 生成访问 URL
        file_url = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{file_key}"
        
        return {
            "file_url": file_url,
            "file_key": file_key
        }
    
    @staticmethod
    def _get_content_type(file_ext: str) -> str:
        """根据扩展名获取 Content-Type"""
        content_types = {
            # 图片
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            # 视频
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'wmv': 'video/x-ms-wmv',
            'flv': 'video/x-flv',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm',
            # 音频
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            # 文本
            'txt': 'text/plain',
            'json': 'application/json',
            'xml': 'application/xml',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        return content_types.get(file_ext, '')
    
    @classmethod
    def delete_file(cls, file_key: str) -> bool:
        """
        删除 OSS 文件
        
        Args:
            file_key: 文件在 OSS 中的路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            bucket = cls.get_bucket()
            bucket.delete_object(file_key)
            return True
        except Exception:
            return False
    
    @classmethod
    def get_file_url(cls, file_key: str) -> str:
        """
        获取文件访问 URL
        
        Args:
            file_key: 文件在 OSS 中的路径
            
        Returns:
            str: 文件访问 URL
        """
        return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{file_key}"
    
    @classmethod
    def get_signed_url(cls, file_key: str, expires: int = 3600) -> str:
        """
        获取带签名的临时访问 URL
        
        Args:
            file_key: 文件在 OSS 中的路径
            expires: 过期时间（秒），默认 1 小时
            
        Returns:
            str: 带签名的访问 URL
        """
        bucket = cls.get_bucket()
        return bucket.sign_url("GET", file_key, expires)
