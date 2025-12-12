import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class DashScopeFileUploader:
    """DashScope 文件上传工具类
    
    用于将本地文件上传到 DashScope 临时存储 OSS，获取可用于 API 调用的 oss:// URL。
    上传的文件有效期为 48 小时。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化上传器
        
        Args:
            api_key: DashScope API Key，如果不提供则从环境变量 DASHSCOPE_API_KEY 获取
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key 未提供，请通过参数传入或设置 DASHSCOPE_API_KEY 环境变量")
        
        self.upload_url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    
    def _get_upload_policy(self, model_name: str) -> Dict[str, Any]:
        """获取文件上传凭证
        
        Args:
            model_name: 模型名称
            
        Returns:
            上传凭证数据
            
        Raises:
            Exception: 获取凭证失败时抛出异常
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        params = {
            "action": "getPolicy",
            "model": model_name
        }
        
        response = requests.get(self.upload_url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"获取上传凭证失败: {response.text}")
        
        return response.json()['data']
    
    def _upload_file_to_oss(self, policy_data: Dict[str, Any], file_path: str) -> str:
        """将文件上传到临时存储OSS
        
        Args:
            policy_data: 上传凭证数据
            file_path: 本地文件路径
            
        Returns:
            OSS URL (oss://<key> 格式)
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        file_name = Path(file_path).name
        key = f"{policy_data['upload_dir']}/{file_name}"
        
        with open(file_path, 'rb') as file:
            files = {
                'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
                'Signature': (None, policy_data['signature']),
                'policy': (None, policy_data['policy']),
                'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
                'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
                'key': (None, key),
                'success_action_status': (None, '200'),
                'file': (file_name, file)
            }
            
            response = requests.post(policy_data['upload_host'], files=files)
            if response.status_code != 200:
                raise Exception(f"文件上传失败: {response.text}")
        
        return f"oss://{key}"
    
    def upload_file(self, file_path: str, model_name: str = "qwen-vl-plus") -> str:
        """上传本地文件到 OSS 并获取 URL
        
        Args:
            file_path: 本地文件路径
            model_name: 模型名称，默认为 "qwen-vl-plus"
            
        Returns:
            OSS URL (oss://<key> 格式)，可直接用于 DashScope API 调用
            
        Raises:
            FileNotFoundError: 文件不存在时抛出
            Exception: 上传过程中发生错误时抛出
            
        Example:
            >>> uploader = DashScopeFileUploader()
            >>> oss_url = uploader.upload_file("/path/to/image.jpg")
            >>> print(oss_url)  # oss://upload_dir/image.jpg
        """
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 1. 获取上传凭证（上传凭证接口有限流，超出限流将导致请求失败）
        policy_data = self._get_upload_policy(model_name)
        
        # 2. 上传文件到OSS
        oss_url = self._upload_file_to_oss(policy_data, file_path)
        
        return oss_url
    
    def upload_file_with_info(self, file_path: str, model_name: str = "qwen-vl-plus") -> Dict[str, Any]:
        """上传文件并返回详细信息
        
        Args:
            file_path: 本地文件路径
            model_name: 模型名称，默认为 "qwen-vl-plus"
            
        Returns:
            包含 OSS URL 和过期时间等信息的字典
            
        Example:
            >>> uploader = DashScopeFileUploader()
            >>> result = uploader.upload_file_with_info("/path/to/image.jpg")
            >>> print(result)
            {
                'oss_url': 'oss://upload_dir/image.jpg',
                'expire_time': '2024-01-03 15:30:00',
                'file_name': 'image.jpg',
                'file_size': 1024000
            }
        """
        oss_url = self.upload_file(file_path, model_name)
        file_path_obj = Path(file_path)
        expire_time = datetime.now() + timedelta(hours=48)
        
        return {
            'oss_url': oss_url,
            'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': file_path_obj.name,
            'file_size': file_path_obj.stat().st_size
        }


if __name__ == "__main__":
    # 使用示例
    try:
        uploader = DashScopeFileUploader()
        
        # 待上传的文件路径（请替换为实际文件路径）
        file_path = "/tmp/cat.png"
        
        # 上传文件并获取详细信息
        result = uploader.upload_file_with_info(file_path)
        
        print(f"文件上传成功！")
        print(f"文件名: {result['file_name']}")
        print(f"文件大小: {result['file_size']} bytes")
        print(f"OSS URL: {result['oss_url']}")
        print(f"过期时间: {result['expire_time']} (48小时有效)")
        print("使用该URL时请参考 DashScope 文档，否则可能出错。")
        
    except Exception as e:
        print(f"上传失败: {str(e)}")
