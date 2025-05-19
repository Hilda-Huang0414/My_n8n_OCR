# n8n OCR 自动化处理工程

## 项目概述

本工程是一个基于n8n的自动化OCR处理系统，能够处理PDF和图片文件，提取其中的商品信息，并与真值表进行模糊匹配验证。

## 工程结构
n8n_project/
└── z_n8n/
├── files/ # 存放输入文件(PDF/图片)和真值表
│ ├── truth_values.xlsx # 商品名称真值表
│ └── ... # 其他输入文件
├── output/ # 处理结果输出目录
├── fuzz_app.py # 主功能服务(Flask应用)
├── webhook_trigger.py # Webhook触发器
├── python_formater.py # Python代码格式化工具
└── My_n8n_OCR.json # n8n工作流配置文件


## 主要功能

1. **OCR信息提取**：从PDF/图片中提取结构化商品信息
2. **模糊匹配**：与真值表进行相似度匹配
3. **自动化处理**：根据匹配结果自动分类存储或发送警报
4. **代码规范化**：统一的Python代码格式化标准

## 组件说明

### 1. fuzz_app.py (主功能服务)

- **功能**：
  - 提供REST API接口处理OCR请求
  - 使用Mistral AI进行OCR处理
  - 实现模糊匹配算法(RapidFuzz)
  - 数据验证(Pydantic模型)

- **API端点**：
  - `/pdfs_ocr` - 处理PDF文件
  - `/images_ocr` - 处理图片文件
  - `/save_json` - 保存处理结果
  - `/chat` - 通用聊天接口

- **使用方法**：
  ```bash
  python fuzz_app.py

### 2. webhook_trigger.py (Webhook触发器)

- **功能**：
  - 自动触发n8n工作流
  - 图片压缩预处理
  - 文件类型自动识别

- **使用方法**：
  ```bash
  python webhook_trigger.py

### 3. My_n8n_OCR.json (n8n工作流)

- **工作流节点**:
  - Webhook接收器
  - 文件类型分流(Switch)
  - OCR处理(HTTP请求)
  - 结果评估(If条件)
  - 成功保存/失败告警

- **特点**：
  - 可视化流程设计
  - 条件分支处理
  - 错误自动通知

### 4. python_formater.py (代码格式化工具)

- **功能**：
  - 自动格式化Python代码

- **使用方法**：
  ```bash
  bash
    # 格式化当前目录
    python python_formater.py
    # 格式化指定目录
    python python_formater.py path/to/directory