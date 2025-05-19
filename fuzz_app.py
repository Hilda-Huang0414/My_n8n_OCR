# -*- coding: utf-8 -*-
import json
import os
from typing import List
import pandas as pd
from flask import Flask, jsonify, request
from mistralai import Mistral
from pydantic import BaseModel, Field
from rapidfuzz import fuzz, process  

app = Flask(__name__)
os.environ["MISTRAL_API_KEY"] = "RQJafCchujxapkPGCw0pPZM3G7J04i7N"
api_key = os.environ["MISTRAL_API_KEY"]
truth_path = "D:/Python_Project/2024/n8n_project/z_n8n/files/truth_values.xlsx"
output_path = "D:/Python_Project/2024/n8n_project/z_n8n/output"

# 定义Pydantic模型（结构化输出）
class OrderItem(BaseModel):
    product_id: str
    original_input: str
    quantity: str

class Order(BaseModel):
    customer_name: str
    items: List[OrderItem]
    status: str


# 模糊匹配
def fuzzy_match_excel_to_json(ocr_data, file_name):
    # 1. 读取Excel真值表
    df_truth = pd.read_excel(truth_path)
    truth_list = df_truth.iloc[:, 1].astype(str).tolist()  # 假设真值在第一列

    # 2. json判断
    if isinstance(ocr_data, str):
        ocr_data = json.loads(ocr_data)  # 如果是字符串，解析为字典

    # 3. 为每个OCR结果添加匹配得分
    for item in ocr_data.get("items", []):
        ocr_text = item.get("original_input", "")
        # 使用RapidFuzz进行快速模糊匹配
        best_match = process.extractOne(
            ocr_text,
            truth_list,
            scorer=fuzz.token_set_ratio,  # 对词序不敏感的更优算法
            score_cutoff=1,  # 最低相似度阈值
        )
        if best_match:
            item["matched_name"] = best_match[0]
            item["confidence"] = "{:.2f}".format(best_match[1])
        else:
            item["matched_name"] = None
            item["confidence"] = None

    # 4. 添加综合处理标志位
    flag = True
    for item in ocr_data.get("items", []):
        confidence = item.get("confidence")

        # 处理confidence为null的情况
        if confidence is None:
            flag = False

        # 处理confidence为字符串的情况（如"100.00"）
        try:
            confidence_float = float(confidence)
        except (ValueError, TypeError):
            flag = False

        # 检查是否低于80
        if confidence_float < 80:
            flag = False

    ocr_data["evaluation"] = flag
    ocr_data["file_name"] = file_name
    json_data = json.dumps(ocr_data, ensure_ascii=False, indent=2)
    return json_data


@app.route("/pdfs_ocr", methods=["POST"])
def pdfs_ocr():
    """使用Mistral AI分析文件并返回结构化数据"""
    # 1. 接收数据和初始化客户端
    data = request.json
    file_name = data.get("file_name")
    pdf_path = data.get("input_data")
    client = Mistral(api_key=api_key)

    # 2. API
    prompt = """從文件中提取商品信息，去除其他信息，仅按以下格式返回：
    {
    "customer_name": "顧客姓名",
    "order_date": "YYYY-MM-DD",
    "items": [
        {
        "product_id": "P001",
        "original_input": "商品名稱",
        "quantity": "數量規格",
        }
    ],
    "status": "状态"
    }
    """

    uploaded_pdf = client.files.upload(
        file={
            "file_name": "uploaded_file.pdf",
            "content": open(f"{pdf_path}", "rb"),
        },
        purpose="ocr",
    )
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{prompt}"},
                {"type": "document_url", "document_url": signed_url.url},
            ],
        }
    ]

    chat_response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        response_format={"type": "json_object"},
    )

    # 3 结构化检查
    json_data = Order.model_validate_json(chat_response.choices[0].message.content)
    ocr_data = json_data.model_dump()
    structured_output = fuzzy_match_excel_to_json(ocr_data, file_name)

    return structured_output


@app.route("/chat", methods=["POST"])
def chat():
    content_data = request.json["content"]
    client = Mistral(api_key=api_key)
    chat_response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": f"{content_data}"}],
    )
    return chat_response.choices[0].message.content


@app.route("/images_ocr", methods=["POST"])
def images_ocr():
    data = request.json
    file_name = data.get("file_name")
    base64_string = data.get("input_data")
    """使用Mistral Pixtral分析图片并返回结构化数据"""
    # 初始化客户端
    client = Mistral(api_key=api_key)

    # 准备图片和提示词
    prompt = """從文件中提取商品信息，去除其他信息，仅按以下格式返回：
    {
    "customer_name": "顧客姓名",
    "order_date": "YYYY-MM-DD",
    "items": [
        {
        "product_id": "P001",
        "original_input": "商品名稱",
        "quantity": "數量規格",
        }
    ],
    "status": "状态"
    }
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{prompt}"},
                {"type": "image_url", "image_url": {"url": f"{base64_string}"}},
            ],
        }
    ]

    chat_response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        response_format={"type": "json_object"},
    )

    json_data = Order.model_validate_json(chat_response.choices[0].message.content)
    ocr_data = json_data.model_dump()
    structured_output = fuzzy_match_excel_to_json(ocr_data, file_name)
    return structured_output


@app.route("/save_json", methods=["POST"])
def save_json():
    data = request.json
    base, ext = f"{data.get('Json_Data').get('file_name')}".split(".")
    ext = ext[1:] if ext.startswith(".") else ext
    output_file = f"{base}_{ext}.json"
    output = os.path.join(output_path, output_file)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return jsonify({"status": "success", "message": "Data saved successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=56781, debug=True)
