# check_answer.py
from extract_text_from_image import extract_text_from_image
from config import base_url, judge_model, api_key, judge_max_tokens
from openai import OpenAI

def extract_brackets_content(s):    # AI 不一定会严格输出JSON，所以需要手动提取
    start = s.find('[')
    end = s.rfind(']')
    if start != -1 and end != -1 and start < end:
        return s[start:end + 1]
    else:
        raise ValueError("No matching brackets found")

def check_answer(image_path, answer, problem_count, logger=lambda x: print(x)):
    logger("正在提取图片中的文字...")
    text = extract_text_from_image(image_path)
    logger("提取到的文字："+text)
    logger("正在判断答案...")
    cilent = OpenAI(api_key=api_key, base_url=base_url)
    example="""[{"analysis":"题目1的解题过程正确。","status":"AC"},
{"analysis":"题目2的解题过程有误。解答不完整。","status":"WA"},
{"analysis":"题目3未找到任何解题过程。","status":"UKE"}]"""
    messages=[
        {
            "role": "user",
            "content":f"请判断下列题目的解题过程是否正确。共有{problem_count}道题目，请依次判断。\
解题过程：{text}，答案：{answer}。输出格式应为一个严格的JSON列表，包含以下字段：analysis（\
对解题过程的分析。），status（字符串AC，WA或UKE：分别代表正确，错误，未知或未找到解题过程）。你\
只需要检查每个问题的最终答案。示例：\
{example}注意：你必须使用严格的JSON格式，不能添加任何多余内容，包括但不限于Markdown代码框。"
        }
    ]
    params={
        "model":judge_model,
        "messages":messages,
        "max_tokens":judge_max_tokens
    }
    response = cilent.chat.completions.create(**params)
    result = extract_brackets_content(response.choices[0].message.content)
    logger("判断结果："+result)

    return result

if __name__ == "__main__":
    print("api_key:",api_key)
    print(check_answer("./app/test.jpg",\
                       "（1）∠M=22.5°（2.1）∠ABE=40°（2.2）∠BFD=(k-1)*300°/k或60°",3))