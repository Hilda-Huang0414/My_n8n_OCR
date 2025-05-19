# -*- coding: utf-8 -*-
import base64
from pathlib import Path

import requests

# 进行图片压缩
from PIL import Image


# 图像预处理(可选)
def compress_image(input_path, output_path, max_size_mb=2, quality=85):
    img = Image.open(input_path)
    # 1. 转换为 RGB（避免 PNG 透明通道问题）
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")

    # 2. 调整大小（可选）
    img.thumbnail((1024, 1024))  # 限制最大边长

    # 3. 保存为 JPEG 并调整质量
    img.save(output_path, "JPEG", quality=quality, optimize=True)

    # 4. 检查是否小于 max_size_mb
    with open(output_path, "rb") as f:
        size_mb = len(f.read()) / (1024 * 1024)
    if size_mb > max_size_mb:
        compress_image(
            input_path, output_path, max_size_mb, quality - 5
        )  # 递归降低质量


if __name__ == "__main__":

    url = "http://localhost:5678/webhook-test/ocr_files"
    file_path = "D:/Python_Project/2024/n8n_project/z_n8n/files"
    # file_name = "3.png"
    file_name = "sap_order_chinese_4.pdf"
    file_pre = Path(file_path, file_name)
    file_suffix = Path(file_name).suffix

    if file_suffix in [".jpeg", ".png", ".jpg"]:  # 返回包含点的后缀如".txt"

        name = str(file_name).split(".")[0]
        # file_pre = file_path + file_name
        file_input = file_path + name + "_comp.jpeg"
        compress_image(file_pre, file_input)
        with open(file_input, "rb") as f:
            binary_data = f.read()  # 获取二进制数据
            base64_str = base64.b64encode(binary_data).decode("utf-8")  # 转换为Base64字符串
            files = {
                "file_name": file_name,
                "file_type": "images",
                "input_data": f"data:image/jpeg;base64,{base64_str}",
            }

    elif file_suffix == ".pdf":
        with open(file_pre, "rb") as f:
            binary_data = f.read()  # 获取二进制数据
            # base64_str = base64.b64encode(binary_data).decode("utf-8")  #
            # 转换为Base64字符串
            files = {
                "file_name": file_name,
                "file_type": "pdf",
                "input_data": f"{file_pre}",
            }
    else:
        files = {"file_name": file_name, "file_type": "Null", "input_data": file_pre}
    # # upload webhook
    response = requests.post(url, files=files)
    print(response.status_code, response.text)