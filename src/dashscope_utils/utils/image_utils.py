from PIL import Image

def compress_image(input_path, output_path, quality=85):
    """压缩图片为JPEG，降低质量以减小文件大小。

    Args:
        input_path (str): 输入图片路径
        output_path (str): 压缩后图片路径
        quality (int): JPEG质量（1-95）
    """
    with Image.open(input_path) as img:
        img = img.convert("RGB")  # 保证是JPEG兼容
        img.save(output_path, "JPEG", optimize=True, quality=quality)