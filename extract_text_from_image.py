from config import base_url, ocr_model, api_key, ocr_max_tokens
from openai import OpenAI
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(image_path):
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=api_key, base_url=base_url)
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
    params = {
        "model": ocr_model,
        "messages": messages,
        "max_tokens": ocr_max_tokens
    }
    result = client.chat.completions.create(**params)
    return result.choices[0].message.content

if __name__ == "__main__":
    print(extract_text_from_image("./app/test.jpg"))