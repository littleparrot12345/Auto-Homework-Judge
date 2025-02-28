from extract_text_from_image import extract_text_from_image
from app.config import base_url, judge_model, api_key, judge_max_tokens
from openai import OpenAI

def check_answer(image_path, answer, problem_count):
    """
    根据给定的图像路径和答案，使用OpenAI的API判断解题过程是否正确。

    参数:
    image_path (str): 图像文件的路径。
    answer (str): 用户的答案。
    problem_count (int): 题目的数量。

    返回:
    str: OpenAI返回的判断结果，格式为JSON字符串。

    具体步骤:
    1. 从图像中提取文本。
    2. 创建OpenAI客户端实例，使用提供的API密钥和基础URL。
    3. 构造示例JSON格式，用于指导OpenAI生成响应。
    4. 构造请求消息，包含题目数量、解题过程和答案。
    5. 设置请求参数，包括模型、消息和最大令牌数。
    6. 发送请求并获取响应。
    7. 返回响应中的消息内容。
    """
    # 从图像中提取文本
    text = extract_text_from_image(image_path)
    # 创建OpenAI客户端实例，使用提供的API密钥和基础URL
    cilent = OpenAI(api_key=api_key, base_url=base_url)
    example="""[{"analysis":"题目1的解题过程正确。","status":"AC"},
{"analysis":"题目2的解题过程有误。解答不完整。","status":"WA"},
{"analysis":"题目3未找到任何解题过程。","status":"UKE"}]"""
    messages=[
        {
            "role": "user",
            "content":f"请判断下列题目的解题过程是否正确。共有{problem_count}道题目，请依次判断。\
解题过程：{text}，答案：{answer}。输出格式应为一个严格的JSON列表，包含以下字段：analysis（\
对解题过程的分析。），status（字符串AC，WA或UKE：分别代表正确，错误，未知或未找到解题过程）示例：\
{example}注意：你必须使用严格的JSON格式，不能添加任何多余内容，包括但不限于Markdown代码框。"
        }
    ]
    params={
        "model":judge_model,
        "messages":messages,
        "max_tokens":judge_max_tokens
    }
    response = cilent.chat.completions.create(**params)
    return response.choices[0].message.content

if __name__ == "__main__":
    print(check_answer("./app/test.jpg","（1）∠ABE=40°（2）∠BFD=(k-1)*300°/k或60°",2))