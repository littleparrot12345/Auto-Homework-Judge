from app.config import base_url, ocr_model, judge_model, api_key
from openai import OpenAI
import base64

def encode_image(image_path):
    """
    将指定路径的图像文件编码为Base64字符串。

    参数:
    image_path (str): 图像文件的路径。

    返回:
    str: 图像文件的Base64编码字符串。

    说明:
    该函数首先打开指定路径的图像文件，以二进制读取模式("rb")。
    然后，使用base64模块对图像文件的内容进行Base64编码。
    最后，将编码后的字节串解码为UTF-8字符串并返回。
    """
    # 打开指定路径的图像文件，以二进制读取模式("rb")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(image_path):
    """
    从图像中提取文本内容。

    参数:
    image_path (str): 图像文件的路径。

    返回:
    str: 从图像中提取的文本内容。

    步骤:
    1. 将图像文件编码为Base64字符串。
    2. 创建OpenAI客户端实例，传入API密钥和基础URL。
    3. 构造消息列表，包含用户请求和图像URL。
    4. 设置请求参数，包括模型名称、消息列表和最大令牌数。
    5. 调用OpenAI客户端的chat.completions.create方法，传入参数。
    6. 返回第一个选择的消息内容，即OCR识别结果。
    """
    # 将图像文件编码为Base64字符串
    base64_image = encode_image(image_path)
    # 创建OpenAI客户端实例，传入API密钥和基础URL
    client = OpenAI(api_key=api_key, base_url=base_url)
    # 构造消息列表，包含用户请求和图像URL
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "识别文字内容。不要用Markdown。不要添加任何多余内容。\
注意包含解题过程和答案（图中已有）。注意，如果图中没有完成题目，则备注。"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    # 设置请求参数，包括模型名称、消息列表和最大令牌数
    params = {
        "model": ocr_model,
        "messages": messages,
        "max_tokens": 512
    }
    # 调用OpenAI客户端的chat.completions.create方法，传入参数
    result = client.chat.completions.create(**params)
    # 返回第一个选择的消息内容，即OCR识别结果
    return result.choices[0].message.content

if __name__ == "__main__":
    print(extract_text_from_image("./app/test.jpg"))