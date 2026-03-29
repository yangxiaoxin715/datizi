import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# ── Step 1 系统提示：只让 R1 解题，不写报告 ──
SOLVE_PROMPT = """你是一个严谨的数学解题引擎。
请仔细解答用户给出的小学数学题，输出：
1. 最终答案（一句话）
2. 完整解题步骤（每步写清楚在算什么、为什么）

要求：
- 必须验算，确保答案正确
- 不要写任何教学建议，只写解题过程
- 如果题目有歧义或条件不足，明确指出"""

# ── Step 2 系统提示：只让 chat 写讲题报告，不碰数学 ──
REPORT_PROMPT = """你是一个"小学生家长讲题备课助手"。

用户消息中已包含【R1解题结果】，这是由专用数学引擎计算并验证的正确答案和步骤。
你的唯一任务是基于这个已验证的解题结果，写一份给家长看的讲题备课报告。

严格规则：
- 禁止重新计算，禁止质疑答案，直接采用【R1解题结果】
- 第1部分"标准答案与步骤"直接整理自【R1解题结果】，不要改动数字和逻辑
- 第2-8部分只写教学建议，不涉及任何数学推导

你的目标是帮助家长：
1. 快速看懂这道题的答案和步骤
2. 知道考什么、孩子容易卡在哪
3. 把题拆成孩子当前年级能懂的台阶
4. 提前知道自己哪里容易讲崩
5. 判断孩子是真懂还是假懂

原则：
- 对象是家长，不是孩子，不要对孩子说"你"
- 必须严格按孩子当前年级水平设计讲法，不能用高年级方法
- 语言简洁、温和、实用，每个模块点到为止
- 全文严格控制在 500 字以内
- 少讲道理，多给直接可用的话

请按固定结构输出，不要省略模块标题。"""


class GenerateRequest(BaseModel):
    grade: str
    question: str
    student_answer: str = ""
    correct_answer: str = ""
    parent_note: str = ""


async def r1_solve(question: str, grade: str) -> str:
    """Step 1：用 deepseek-reasoner 解题，返回完整解题结果。"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": SOLVE_PROMPT},
                    {"role": "user", "content": f"年级：{grade}\n\n题目：{question}"},
                ],
                "max_tokens": 1000,
                "temperature": 0,
            },
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def build_report_prompt(req: GenerateRequest, solution: str) -> str:
    return f"""请基于以下信息生成一份"家长讲题备课报告"。

【孩子年级】
{req.grade}

【题目】
{req.question}

【孩子原答案】
{req.student_answer or "未填写"}

【家长补充说明】
{req.parent_note or "未填写"}

【R1解题结果（已验证正确，直接使用，禁止重新计算）】
{solution}

请严格按照以下结构输出：

## 1. 标准答案与步骤
## 2. 核心考点
## 3. 孩子最容易卡住的地方
## 4. 讲题梯子
## 5. 讲明白三步（先说出来、再写出来、最后画出来）
## 6. 家长辅导话术建议
## 7. 家长避坑提醒
## 8. 讲完后可练的1-2道同类小题（附答案）

要求：
- 第1部分直接整理自上方R1解题结果，保持数字和步骤一致
- 第2-8部分只写教学建议，不推导数学
- 每个模块只写最关键的 2-3 个要点，不展开
- 全文 500 字以内
- 多给直接可用的话，少讲空泛道理"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/jinkuang", response_class=HTMLResponse)
async def jinkuang():
    with open("static/jinkuang.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/generate")
async def generate(req: GenerateRequest):

    async def stream():
        try:
            # ── Step 1：R1 解题（非流式，确保答案准确）──
            if req.correct_answer:
                # 家长已知答案，跳过 R1，直接用
                solution = f"答案（家长提供）：{req.correct_answer}"
            else:
                solution = await r1_solve(req.question, req.grade)

            # ── Step 2：chat 写报告（流式输出）──
            report_prompt = build_report_prompt(req, solution)

            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": REPORT_PROMPT},
                            {"role": "user", "content": report_prompt},
                        ],
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            yield "data: [DONE]\n\n"
                            return
                        if not data_str:
                            continue
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0]["delta"]
                            content = delta.get("content") or ""
                            if content:
                                yield f"data: {json.dumps({'text': content}, ensure_ascii=False)}\n\n"
                        except Exception:
                            pass

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
