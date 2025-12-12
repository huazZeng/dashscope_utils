from typing import Optional
from .dashscope_file_uploader import DashScopeFileUploader


def upload_file_to_oss(file_path: str, model_name: str = "qwen-vl-plus", 
                      api_key: Optional[str] = None) -> str:
    """上传文件到 OSS 的便捷函数
    
    Args:
        file_path: 本地文件路径
        model_name: 模型名称，默认为 "qwen-vl-plus"
        api_key: API Key，如果不提供则从环境变量获取
        
    Returns:
        OSS URL (oss://<key> 格式)
        
    Example:
        >>> from dashscope_utils.utils import upload_file_to_oss
        >>> oss_url = upload_file_to_oss("/path/to/image.jpg")
        >>> print(oss_url)
    """
    uploader = DashScopeFileUploader(api_key)
    return uploader.upload_file(file_path, model_name)
