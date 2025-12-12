import os
import tempfile
from typing import Any, Dict, List, Union
from urllib.parse import urlparse, unquote

from .image_utils import compress_image
from .upload_helpers import upload_file_to_oss


def _is_local_file_url(url: str) -> bool:
    """检测URL是否为file:///本地路径且存在。"""
    if not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme != "file":
            return False
        local_path = unquote(parsed.path)
        if parsed.fragment:
            local_path += "#" + parsed.fragment
        return os.path.exists(local_path)
    except Exception:
        return False


def process_image(image_url: str, max_size_mb: int = 10, temp_dir: str = None) -> str:
    """处理单个图像文件
    
    Args:
        image_url: 图像URL (file://、http://、https://或oss://格式)
        max_size_mb: 最大文件大小(MB)，超过则压缩
        temp_dir: 临时文件存储目录，默认使用系统临时目录
        
    Returns:
        处理后的图像URL
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    # 如果是网络URL或OSS URL，直接返回
    if image_url.startswith(('http://', 'https://', 'oss://')):
        return image_url
    
    if not _is_local_file_url(image_url):
        raise FileNotFoundError(f"本地 image 路径不存在: {image_url}")
    
    image_path = unquote(urlparse(image_url).path)
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(image_path)
    
    if file_size > max_size_bytes:
        # 需要压缩
        ratio = max_size_bytes / file_size
        base_quality = 85
        quality = max(int(base_quality * ratio), 20)
        
        # 使用指定的临时目录或系统默认目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=temp_dir) as tmpf:
            compressed_path = tmpf.name
        compress_image(image_path, compressed_path, quality=quality)
        return "file://" + compressed_path
    else:
        return "file://" + image_path


def process_video_frames(video_frames: List[str], max_size_mb: int = 10, temp_dir: str = None) -> List[str]:
    """处理视频帧列表（每一帧是图片）
    
    Args:
        video_frames: 视频帧URL列表
        max_size_mb: 每张图片最大文件大小(MB)
        temp_dir: 临时文件存储目录，默认使用系统临时目录
        
    Returns:
        处理后的视频帧URL列表
    """
    new_frames = []
    for img_url in video_frames:
        # 如果是网络URL或OSS URL，直接返回
        if img_url.startswith(('http://', 'https://', 'oss://')):
            new_frames.append(img_url)
        else:
            processed_url = process_image(img_url, max_size_mb, temp_dir)
            new_frames.append(processed_url)
    return new_frames


def process_video_file(video_url: str, api_key: str, model_name: str = "qwen-vl-plus") -> str:
    """处理单个视频文件
    
    Args:
        video_url: 视频URL (file://、http://、https://或oss://格式)
        api_key: API密钥
        model_name: 模型名称
        
    Returns:
        处理后的视频URL (file://或oss://格式)
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        ValueError: 文件过大时抛出
    """
    # 如果是网络URL或OSS URL，直接返回
    if video_url.startswith(('http://', 'https://', 'oss://')):
        return video_url
    
    if not _is_local_file_url(video_url):
        raise FileNotFoundError(f"本地 video 路径不存在: {video_url}")
    
    video_path = unquote(urlparse(video_url).path)
    max_size_bytes = 100 * 1024 * 1024  # 100MB
    max_upload_size_bytes = 2 * 1024 * 1024 * 1024  # 2GB
    file_size = os.path.getsize(video_path)
    
    if file_size > max_size_bytes:
        if file_size < max_upload_size_bytes:
            # 文件大小在 100MB - 2GB 之间，上传到 OSS
            oss_url = upload_file_to_oss(video_path, model_name, api_key)
            return oss_url
        else:
            raise ValueError(f"视频文件过大 ({file_size / 1024 / 1024 / 1024:.1f}GB)，超过 2GB 限制")
    else:
        return "file://" + video_path


def process_media_content(content: List[Dict[str, Any]], api_key: str, model_name: str = "qwen-vl-plus", temp_dir: str = None) -> List[Dict[str, Any]]:
    """处理多模态内容中的媒体文件
    
    Args:
        content: 多模态内容列表
        api_key: API密钥
        model_name: 模型名称
        temp_dir: 临时文件存储目录，默认使用系统临时目录
        
    Returns:
        处理后的内容列表
    """
    if not isinstance(content, list):
        return content
    
    for entry in content:
        if not isinstance(entry, dict):
            continue
            
        # 处理图像
        if "image" in entry:
            entry["image"] = process_image(entry["image"], temp_dir=temp_dir)
        
        # 处理视频
        if "video" in entry:
            video_value = entry["video"]
            if isinstance(video_value, list):
                # 视频帧列表
                entry["video"] = process_video_frames(video_value, temp_dir=temp_dir)
            else:
                # 单个视频文件
                entry["video"] = process_video_file(video_value, api_key, model_name)
    
    return content
