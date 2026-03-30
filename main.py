import json
import os
import re

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

GRADE_POLICIES = {
    "一年级": {
        "allowed": ["20以内加减", "看图数数", "简单比较", "凑十与拆分", "直观图示"],
        "forbidden": ["乘除法", "方程", "分数", "小数", "复杂数量关系"],
        "ceiling": "只允许使用一年级及以下已学内容，必须依赖直观图示、数数、拆分、简单加减。",
    },
    "二年级": {
        "allowed": ["表内乘除", "简单倍数关系", "长度时间人民币基础题", "两步以内数量关系"],
        "forbidden": ["方程", "分数应用题", "小数", "复杂比例关系"],
        "ceiling": "只允许使用二年级及以下已学内容，优先乘除意义、倍数关系和直观数量变化。",
    },
    "三年级": {
        "allowed": ["万以内数", "乘除法竖式", "简单分数初步", "周长面积初步", "两三步数量关系"],
        "forbidden": ["方程", "小数运算", "比例", "复杂行程与工程"],
        "ceiling": "只允许使用三年级及以下已学内容，优先整数运算、简单分数直观理解和基础数量关系。",
    },
    "四年级": {
        "allowed": ["整数四则运算", "份数思维", "倍数关系", "对应关系", "数量关系分析"],
        "forbidden": ["方程", "用字母表示未知数", "分数方程", "比例法"],
        "ceiling": "只允许使用四年级及以下已学内容，优先份数、倍数、对应关系和数量关系，不得使用方程。",
    },
    "五年级": {
        "allowed": ["小数", "分数基础", "简易方程初步", "平均数", "较完整数量关系"],
        "forbidden": ["比例法", "超纲代数技巧", "复杂方程组"],
        "ceiling": "只允许使用五年级及以下已学内容，可以使用简易方程，但不能使用比例法和更高年级代数技巧。",
    },
    "六年级": {
        "allowed": ["分数应用题", "比和比例初步", "稍复杂方程", "较复杂数量关系"],
        "forbidden": ["初中代数", "二元一次方程组", "函数", "几何证明"],
        "ceiling": "只允许使用六年级及以下已学内容，可以使用分数、比例初步和稍复杂方程，但不能跨到初中方法。",
    },
}

# ── Step 1 系统提示：只让 R1 解题，不写报告 ──
SOLVE_PROMPT = """你是一个严谨的小学数学解题引擎。
请仔细解答用户给出的小学数学题，输出：
1. 最终答案（一句话）
2. 完整解题步骤（每步写清楚在算什么、为什么）

要求：
- 必须验算，确保答案正确
- 不要写任何教学建议，只写解题过程
- 如果题目有歧义或条件不足，明确指出
- 不要使用 LaTeX，不要输出 \\frac、\\quad、\\text 这类数学排版命令，只用普通文本算式"""

GRADE_GUARD_PROMPT = """你是“小学数学年级边界审查器”。

你的任务不是解题，而是判断：这道题能不能用该年级及以下已经学过的方法解决。

你必须严格遵守：
- 只根据“当前年级通常已学知识”判断，不要因为题目能算出来就放宽标准
- 能解，必须说明“只允许的方法”
- 不能解，必须说明“为什么超纲”，以及“等孩子学会什么以后才能解”
- 不允许模糊表述，不允许“勉强可以”“大概可以”
- 只输出一个 JSON 对象，不要输出 markdown，不要输出解释文字

JSON 格式固定为：
{{
  "is_in_scope": true,
  "reason": "一句话说明为什么可解或为什么超纲",
  "missing_knowledge": ["如果超纲，这里列出还没学的前置知识；可解时给空数组"],
  "suggested_grade": "如果超纲，写更合适的年级；可解时仍写当前年级",
  "allowed_method": "这道题在当前年级允许采用的讲法路径，一句话",
  "forbidden_method": "这道题当前年级绝对不能偷用的更高年级方法，一句话"
}}"""

# ── Step 2 系统提示：只让 chat 写讲题报告，不碰数学 ──
REPORT_PROMPT = """你是“搭梯子”的家长讲题副驾。

用户消息中已包含【R1解题结果】，这是由专用数学引擎计算并验证的正确答案和步骤。
你的唯一任务是基于这个已验证的解题结果，写一份给家长看的“讲题副驾卡”。

这不是普通题解，也不是给孩子看的讲义。你的任务是帮助家长在开口讲题前，先知道：
1. 这题现在先讲什么
2. 孩子最可能卡在哪
3. 家长第一句怎么开口
4. 如果孩子没懂，应该怎么退一步讲
5. 最后再看标准答案和步骤

严格规则：
- 禁止重新计算，禁止质疑答案，直接采用【R1解题结果】
- “标准答案与步骤”直接整理自【R1解题结果】，不要改动数字和逻辑
- 其余部分只写讲题建议，不做新的数学推导
- 标准答案不能放在最前面主导整份输出

写作原则：
- 对象是家长，不是孩子，不要对孩子说“你”
- 语言必须口语化、直接、能马上开口
- 不要写教师培训腔，不要写“本题考查了”
- 必须严格按孩子当前年级设计讲法，不能偷用高年级表达
- 必须严格服从“允许方法 / 禁止方法 / 是否超纲”的判断，不能越界
- 少讲道理，多给可直接照着说的话
- 全文尽量简洁，控制在 700 字以内
- 不要输出 LaTeX，不要输出 \\frac、\\quad、\\text、[ ... ] 这类数学排版符号，只用普通文本算式

请按固定结构输出，不要省略模块标题。"""

OUT_OF_SCOPE_PROMPT = """你是“搭梯子”的年级边界说明助手。

你的任务是告诉家长：这道题为什么超出当前年级，孩子还没学到哪里，等学会哪些前置知识后才能做。

严格规则：
- 明确说“这题超出当前年级常规学习范围”
- 明确说“不是孩子笨，是还没学到这个方法”
- 明确列出 2-4 个前置知识点
- 明确说明更适合从几年级开始解决
- 不要给完整题解，不要偷讲高年级解法
- 语言要让家长安心、边界清楚、可执行
- 不要输出 LaTeX，不要输出数学排版命令

请按固定结构输出，不要省略模块标题。"""


class GenerateRequest(BaseModel):
    grade: str
    question: str
    student_answer: str = ""
    correct_answer: str = ""
    parent_note: str = ""


def grade_policy_text(grade: str) -> str:
    policy = GRADE_POLICIES.get(grade)
    if not policy:
        return "请严格按当前年级常规教学边界判断，不能偷用更高年级方法。"
    allowed = "、".join(policy["allowed"])
    forbidden = "、".join(policy["forbidden"])
    return f"{policy['ceiling']} 允许方法：{allowed}。不得使用{forbidden}。"


def sanitize_report_text(text: str) -> str:
    cleaned = text
    while True:
        updated = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", cleaned)
        if updated == cleaned:
            break
        cleaned = updated
    cleaned = re.sub(r"\\text\s*\{([^{}]+)\}", r"\1", cleaned)
    cleaned = cleaned.replace("\\quad", " ")
    cleaned = cleaned.replace("\\(", "").replace("\\)", "")
    cleaned = cleaned.replace("\\[", "").replace("\\]", "")
    cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = cleaned.replace("{", "").replace("}", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def extract_json_object(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


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


async def assess_grade_fit(question: str, grade: str) -> dict:
    policy_text = grade_policy_text(grade)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": GRADE_GUARD_PROMPT},
                    {
                        "role": "user",
                        "content": f"【当前年级】\n{grade}\n\n【年级边界】\n{policy_text}\n\n【题目】\n{question}",
                    },
                ],
                "max_tokens": 500,
                "temperature": 0,
            },
        )
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        assessment = extract_json_object(raw)
        assessment.setdefault("is_in_scope", False)
        assessment.setdefault("reason", "未能完成年级判断")
        assessment.setdefault("missing_knowledge", [])
        assessment.setdefault("suggested_grade", grade)
        assessment.setdefault("allowed_method", "")
        assessment.setdefault("forbidden_method", "")
        return assessment


def build_report_prompt(req: GenerateRequest, solution: str, assessment: dict) -> str:
    return f"""请基于以下信息生成一份“讲题副驾卡”。

【孩子年级】
{req.grade}

【年级边界】
{grade_policy_text(req.grade)}

【年级判断】
可解：{assessment.get("is_in_scope")}
原因：{assessment.get("reason")}
允许方法：{assessment.get("allowed_method")}
禁止方法：{assessment.get("forbidden_method")}

【题目】
{req.question}

【孩子原答案】
{req.student_answer or "未填写"}

【现场补充说明】
{req.parent_note or "未填写"}

【R1解题结果（已验证正确，直接使用，禁止重新计算）】
{solution}

请严格按照以下结构输出：

## 1. 先别急着讲，这题先抓什么
## 2. 孩子最可能卡在哪
## 3. 家长第一句可以怎么开口
## 4. 如果孩子没懂，怎么退一步讲
## 5. 讲题顺序（最多3步）
## 6. 家长最容易讲崩的地方
## 7. 标准答案与步骤
## 8. 讲完后怎么确认孩子是真懂了

要求：
- 第1-6部分必须优先服务“家长现在怎么讲”
- 第7部分直接整理自上方R1解题结果，保持数字和步骤一致
- 第8部分给1-2个检查理解的小问题，不要再出完整练习题
- 必须只使用当前年级允许的方法，不能越界
- 如果这道题更适合用高年级方法，就不要偷偷使用，直接留在允许方法范围内表达
- 所有内容都要简洁，优先给家长能直接照着说的话
- 每个模块只写最关键的 2-3 个要点，不展开"""


def build_out_of_scope_prompt(grade: str, question: str, assessment: dict) -> str:
    missing = assessment.get("missing_knowledge") or []
    missing_lines = "\n".join([f"- {item}" for item in missing]) or "- 当前信息不足，建议补充前置知识判断"
    return f"""请基于以下信息，写一份“超纲说明卡”。

【孩子年级】
{grade}

【题目】
{question}

【年级边界】
{grade_policy_text(grade)}

【超纲原因】
{assessment.get("reason")}

【还没学到的关键知识】
{missing_lines}

【更适合的起点年级】
{assessment.get("suggested_grade", grade)}

请严格按照以下结构输出：

## 1. 这题为什么现在还讲不了
## 2. 不是孩子笨，而是还没学到哪里
## 3. 等孩子学会什么，这题就能开始解
## 4. 家长现在更适合怎么做

要求：
- 必须明确说“这题超出{grade}常规学习范围”
- 必须明确说“等孩子学会……”再接上前置知识
- 不要给完整题解
- 不要出现高年级公式、方程或 LaTeX
- 每个模块只写最关键的 2-3 个要点，不展开"""


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
            assessment = await assess_grade_fit(req.question, req.grade)

            if assessment.get("is_in_scope"):
                if req.correct_answer:
                    solution = f"答案（家长提供）：{req.correct_answer}"
                else:
                    solution = await r1_solve(req.question, req.grade)
                system_prompt = REPORT_PROMPT
                report_prompt = build_report_prompt(req, solution, assessment)
            else:
                system_prompt = OUT_OF_SCOPE_PROMPT
                report_prompt = build_out_of_scope_prompt(req.grade, req.question, assessment)

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
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": report_prompt},
                        ],
                        "stream": True,
                        "temperature": 0,
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
                                yield f"data: {json.dumps({'text': sanitize_report_text(content)}, ensure_ascii=False)}\n\n"
                        except Exception:
                            pass

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
