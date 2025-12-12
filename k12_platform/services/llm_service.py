"""LLM服务 - 调用OpenAI标准接口"""
import json
import base64
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        self.model = OPENAI_MODEL
    
    def solve_math_question(self, question: str, image_base64: str = None) -> dict:
        """解答数理题目，返回分步骤解析"""
        messages = [
            {
                "role": "system",
                "content": """你是一位专业的K12教育辅导老师，擅长解答数学和理科题目。
请按以下格式回答：
1. 先给出最终答案
2. 然后分步骤详细解析，每一步都要清晰说明
3. 指出涉及的知识点
4. 给出类似题目的解题思路

请用JSON格式返回：
{
    "answer": "最终答案",
    "steps": ["步骤1：...", "步骤2：...", ...],
    "knowledge_points": ["知识点1", "知识点2"],
    "tips": "解题技巧提示"
}"""
            }
        ]
        
        if image_base64:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": question or "请解答图片中的题目"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": question})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            # 尝试解析JSON
            try:
                # 提取JSON部分
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content)
            except:
                return {
                    "answer": content,
                    "steps": [],
                    "knowledge_points": [],
                    "tips": ""
                }
        except Exception as e:
            return {"error": str(e)}
    
    def review_essay(self, title: str, content: str, essay_type: str) -> dict:
        """作文批改"""
        messages = [
            {
                "role": "system",
                "content": """你是一位资深的语文老师，擅长作文批改和写作指导。
请从以下几个方面评价作文：
1. 审题立意（针对标题的理解和主题把握）
2. 结构（开头、主体、结尾的组织）
3. 语法（句子通顺、标点正确）
4. 用词（词汇丰富度、准确性）
5. 内容（主题明确、论述有力）

请用JSON格式返回：
{
    "overall_score": 85,
    "topic_analysis": {
        "possible_themes": ["可选主题1", "可选主题2", "可选主题3"],
        "examiner_purpose": "分析出题人的目的和考查重点",
        "key_points": "此作文应该突出的核心要点",
        "common_mistakes": ["审题误解的常见方向1", "审题误解的常见方向2"]
    },
    "structure": {
        "score": 80,
        "feedback": "结构方面的具体评价",
        "suggestions": ["建议1", "建议2"]
    },
    "grammar": {
        "score": 90,
        "feedback": "语法方面的具体评价",
        "errors": ["错误1", "错误2"]
    },
    "vocabulary": {
        "score": 85,
        "feedback": "用词方面的具体评价",
        "highlights": ["亮点词句1"],
        "improvements": ["可以改进的地方"]
    },
    "overall_feedback": "总体评价",
    "suggestions": ["修改建议1", "修改建议2"]
}"""
            },
            {
                "role": "user",
                "content": f"请批改这篇{essay_type}：\n\n标题：{title}\n\n{content}"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content)
            except:
                return {"overall_feedback": content, "overall_score": 0}
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, messages: list, system_prompt: str = None) -> str:
        """聊天助手"""
        chat_messages = []
        
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        else:
            chat_messages.append({
                "role": "system",
                "content": """你是一位友善的学习助手，可以帮助中小学生解答学习和生活中的问题。
你的回答应该：
1. 通俗易懂，适合学生理解
2. 积极正面，给予鼓励
3. 如果涉及学习问题，给出具体的方法建议
4. 如果涉及生活问题，给出合理的建议和引导"""
            })
        
        chat_messages.extend(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                temperature=0.8,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，出现了一些问题：{str(e)}"
    
    def recommend_exercises(self, weak_points: list, subject: str) -> list:
        """根据薄弱知识点推荐练习题"""
        messages = [
            {
                "role": "system",
                "content": """你是一位教育专家，请根据学生的薄弱知识点生成针对性的练习题。
请用JSON格式返回3道练习题：
[
    {
        "question": "题目内容",
        "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
        "answer": "A",
        "explanation": "详细解析",
        "knowledge_point": "涉及的知识点",
        "difficulty": 3
    }
]"""
            },
            {
                "role": "user",
                "content": f"学科：{subject}\n薄弱知识点：{', '.join(weak_points)}\n请生成3道针对性练习题。"
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content)
            except:
                return []
        except Exception as e:
            return []


# 全局实例
llm_service = LLMService()
