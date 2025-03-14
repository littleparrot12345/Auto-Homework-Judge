# config.py
# API Key
# 推荐使用SiliconFlow API。获取方式：
# 1.访问 https://cloud.siliconflow.cn/i/GvBaDbcJ 注册。
# 2.前往 https://cloud.siliconflow.cn/account/ak 新建API Key。
# 3.将API Key填入此处。
# 为了方便开发，此处使用环境变量，实际使用时建议直接填入字符串。
# api_key="your_api_key"
import os
api_key=os.environ.get("AHJ_API_KEY")
# 大语言模型API base URL
# 推荐使用SiliconFlow API。如果使用其它API，请自行修改。
base_url="https://api.siliconflow.cn/v1"
# 进行OCR识别的模型名称
# 必须支持图片。如果使用其它模型，请自行修改。
# 在测试时，默认模型每次调用需要0.0657元。
ocr_model="Qwen/Qwen2-VL-72B-Instruct"
# 进行题目批改的模型名称
# 建议使用DeepSeek-V3。如果使用其它模型，请自行修改。
# 在测试时，默认模型每次调用需要0.0038元。
# 注意：在未实名认证时，每天限制调用100次。
# 如果在使用时经常遇到问题，可以更改为：
# judge_model="Qwen/Qwen2.5-72B-Instruct"
judge_model="deepseek-ai/DeepSeek-V3"
# OCR识别时的最大token数
# 如果在OCR识别时发现结果不完整，可以尝试增加此值。
ocr_max_tokens=512
# 题目批改时的最大token数
# 如果在题目批改时发现结果不完整，可以尝试增加此值。
judge_max_tokens=512
# 自动保存间隔（秒）
autosave_interval=60
# 版本号
# 请勿更改。
version="1.0"