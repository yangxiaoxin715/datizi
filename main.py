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

SYSTEM_PROMPT = """你是一个"小学生家长讲题备课助手"。

你的任务不是直接给孩子讲题，也不是只给标准答案，而是根据家长提供的一道小学数学题，生成一份"家长讲题备课报告"。

你的目标是帮助家长：
1. 快速看懂这道题；
2. 知道这道题在考什么；
3. 预判孩子最容易卡住的地方；
4. 把这道题拆成符合孩子当前年级认知水平的讲解台阶；
5. 用孩子听得懂的方式讲出来；
6. 提前避开讲题时最容易引发混乱、着急、亲子冲突的地方；
7. 帮家长判断孩子到底是真懂还是假懂。

请严格遵守以下原则：

一、你输出的对象是"家长"，不是孩子。
所以语气应该是对家长说话，不要直接对孩子说"你"。

二、必须严格按照孩子当前年级的理解水平来设计讲法。
不能默认调用高于该年级的知识背景，不能使用过于抽象、压缩、高阶的表达方式。
如果这道题家长可能会自然联想到更高阶方法，也要主动提醒：不建议这样讲给当前年级孩子听。

三、你不是普通题解工具。
不要只给答案和标准解析。
你必须输出"怎么讲、先讲什么、孩子可能卡在哪、家长哪里最容易讲崩"。

四、讲题逻辑必须体现"搭梯子"思路。
也就是：
- 先明确孩子当前需要的背景台阶；
- 再一步一步往上搭；
- 不允许一上来直接跳到最终高阶理解。

五、请优先帮助家长获得"我懂了，我知道怎么教了"的掌控感。
报告必须清晰、结构化、实用、可直接用于讲题前备课。

六、【重要】答案已经由专用数学引擎预先验证，会在用户输入中以【预验证答案】标注。
你必须严格采用该答案，不得重新计算，不得质疑，不得在报告中显示任何不确定或自我修正。
如果没有预验证答案，则自己仔细解题，确保正确后再生成报告。

七、请把"三元表征"翻译成家长可直接使用的"讲明白三步"：
1）先说出来；
2）再写出来；
3）最后画出来。
不要只讲概念，要写清家长具体如何用它来判断孩子有没有真正听懂。

八、请尽量使用简洁、清楚、温和的中文表达。
不要空泛，不要套话，不要只讲概念。
每一部分都要具体到家长能直接使用。
全文严格控制在 900-1200 字，不要超出。

请按固定结构输出，不要省略模块标题。"""


class GenerateRequest(BaseModel):
    grade: str
    question: str
    student_answer: str = ""
    correct_answer: str = ""
    parent_note: str = ""


async def presolve_math(question: str, grade: str) -> str:
    """用 deepseek-reasoner 预先算出正确答案，超时则降级到 deepseek-chat。"""
    prompt = (
        f"请严格计算这道{grade}数学题，给出正确答案和关键步骤（150字以内，不需要解释背景）：\n\n{question}"
    )
    for model in ["deepseek-reasoner", "deepseek-chat"]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 600,
                        "temperature": 0,
                    },
                )
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            continue
    return ""


def build_user_prompt(req: GenerateRequest, verified_answer: str = "") -> str:
    answer_block = ""
    if verified_answer:
        answer_block = f"""
【预验证答案（数学引擎已确认，请直接采用，不要重新计算）】
{verified_answer}
"""
    elif req.correct_answer:
        answer_block = f"""
【正确答案（家长提供）】
{req.correct_answer}
"""

    return f"""请根据下面的信息，生成一份"家长讲题备课报告"。

【孩子年级】
{req.grade}

【题目】
{req.question}
{answer_block}
【孩子原答案（可选）】
{req.student_answer or "未填写"}

【家长补充说明（可选）】
{req.parent_note or "未填写"}

请严格按照以下结构输出：

## 1. 标准答案与步骤
## 2. 核心考点
## 3. 孩子最容易卡住的地方
## 4. 讲题梯子
## 5. 讲明白三步（先说出来、再写出来、最后画出来）
## 6. 家长辅导话术建议
## 7. 家长避坑提醒
## 8. 讲完后可练的1-2道同类小题（附答案）

补充要求：
- "讲题梯子"必须分步骤写，清楚说明先讲什么、后讲什么；
- "讲明白三步"必须明确说明：家长怎么用语言、算式、图形来判断孩子是不是真懂；
- "家长辅导话术建议"必须给出可直接拿来讲的句子；
- "家长避坑提醒"必须包含"如果孩子卡住了，应该怎么退回来讲"；
- 语言必须适合小学生家长阅读，不要太学术；
- 全文严格控制在 900-1200 字，每个模块点到为止，不要铺开；
- 少讲空泛道理，多给直接可用的话。"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/jinkuang", response_class=HTMLResponse)
async def jinkuang():
    with open("static/jinkuang.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    # 第一步：用 reasoner 预解题，确保答案正确
    verified_answer = await presolve_math(req.question, req.grade)
    user_prompt = build_user_prompt(req, verified_answer)

    async def stream():
        try:
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
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 3000,
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
                            content = delta.get("content", "")
                            if content:
                                yield f"data: {json.dumps({'text': content}, ensure_ascii=False)}\n\n"
                        except Exception:
                            pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
