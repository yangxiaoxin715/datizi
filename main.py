import json
import os
import re

import httpx
from curriculum_rules import TRACK_LABELS, infer_missing_knowledge, topic_boundary_text, track_policy_text
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

这不是普通题解，也不是给孩子看的讲义，更不是一份备课资料。你的任务是把顶级名师讲这一题时会先抓什么、怎么开口、怎么层层讲透，翻成家长能直接照着用的讲法，帮助家长在开口讲题前，先知道：
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
    actual_grade: str
    learning_level: str
    track: str = "sync"
    question: str
    student_answer: str = ""
    correct_answer: str = ""
    parent_note: str = ""
    current_topic: str = ""


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


async def r1_solve(question: str, learning_level: str) -> str:
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
                    {"role": "user", "content": f"当前学习水平：{learning_level}\n\n题目：{question}"},
                ],
                "max_tokens": 1000,
                "temperature": 0,
            },
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def assess_grade_fit(question: str, actual_grade: str, learning_level: str, current_topic: str, track: str) -> dict:
    policy_text = track_policy_text(track, learning_level)
    topic_text = topic_boundary_text(current_topic, track)
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
                        "content": (
                            f"【孩子实际年级】\n{actual_grade}\n\n"
                            f"【当前路线】\n{TRACK_LABELS.get(track, track)}\n\n"
                            f"【当前学习水平】\n{learning_level}\n\n"
                            f"【当前学习主题】\n{current_topic or '未填写'}\n\n"
                            f"【学习水平边界】\n{policy_text}\n\n"
                            f"【知识点边界】\n{topic_text}\n\n"
                            f"【题目】\n{question}"
                        ),
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
        assessment.setdefault("suggested_grade", learning_level)
        assessment.setdefault("allowed_method", "")
        assessment.setdefault("forbidden_method", "")
        return assessment


def build_report_prompt(req: GenerateRequest, solution: str, assessment: dict) -> str:
    return f"""请基于以下信息生成一份“顶级名师讲题卡”。

目标不是再给一份解析，而是先抓住这道题最关键的审题问题，再把这道题讲透，并让家长照着讲也能讲得像样。

【孩子实际年级】
{req.actual_grade}

【当前路线】
{TRACK_LABELS.get(req.track, req.track)}

【当前学习水平】
{req.learning_level}

【学习水平边界】
{track_policy_text(req.track, req.learning_level)}

【学习水平判断】
可解：{assessment.get("is_in_scope")}
原因：{assessment.get("reason")}
允许方法：{assessment.get("allowed_method")}
禁止方法：{assessment.get("forbidden_method")}

【当前学习主题】
{req.current_topic or "未填写"}

【题目】
{req.question}

【孩子原答案】
{req.student_answer or "未填写"}

【现场补充说明】
{req.parent_note or "未填写"}

【R1解题结果（已验证正确，直接使用，禁止重新计算）】
{solution}

请严格按照以下结构输出：

【结论】
状态：一句话判断，只能二选一“可以按当前水平讲”或“这题先别硬讲”
先抓：只写这题最先该抓的1个关键点，不超过12个字
最后求什么：只写题目最后真正要求的量，不超过12个字
开口：只写家长现在第一句该怎么说，不超过30个字

## 1. 审题焦点
## 2. 审题雷区
## 3. 最后一问真正求什么
## 4. 这题真正的数学钉子
## 5. 孩子最可能卡在哪一步
## 6. 家长第一句怎么说
## 7. 如果孩子没懂，怎么退一步讲
## 8. 讲题顺序（最多3步）
## 9. 标准答案与步骤
## 10. 这题讲完要带走什么方法

要求：
- 这不是普通题解，也不是教师培训稿，而是把顶级名师讲这一题时会先抓什么、怎么开口、怎么层层讲透，翻成家长能直接照着用的讲法
- 必须先写“审题焦点”，指出这题最该先盯住的条件、词或关系
- 必须写“审题雷区”，明确指出孩子最容易把哪句话看偏，以及容易看偏成什么
- 必须写“最后一问真正求什么”，明确说出这题最后问的是哪一种量，不是哪一种量
- “这题真正的数学钉子”必须指出这题背后的核心关系，比如总量不变、差量关系、对应关系、单位1、份数关系等
- 第6部分必须给家长可直接照着说的话，不要写老师腔
- 第7部分必须给具体退法，必要时可以用图、比方、动作或更低门槛的说法
- 第8部分最多3步，每一步只讲最关键动作
- 第9部分直接整理自上方R1解题结果，保持数字和逻辑一致，不要重新计算
- 第10部分必须总结成一句“以后再见到这类题，也可以先这样想”的方法
- 必须只使用当前学习水平允许的方法，不能越界
- 如果这道题更适合用高年级方法，就不要偷偷使用，直接留在允许方法范围内表达
- 如果当前学习水平明显高于实际年级，可以提醒“按当前学习进度可以讲，但讲的时候要更慢、更直观”
- 如果当前路线是“同年级拔高”，允许使用该年级拔高边界内的方法，但仍不能越界到更高年级或初中
- 不要输出 LaTeX，不要输出 \\frac、\\quad、\\text、[ ... ] 这类数学排版符号，只用普通文本算式
- 如果输出里只有步骤、没有审题问题，视为不合格
- 如果输出里只有答案、没有“讲完要带走什么方法”，视为不合格
- 所有内容都要简洁，优先给家长能直接照着说的话
- 每个模块只写最关键的2-3个要点，不展开"""


def build_out_of_scope_prompt(actual_grade: str, learning_level: str, current_topic: str, question: str, assessment: dict, track: str) -> str:
    missing = assessment.get("missing_knowledge") or []
    if not missing:
        missing = infer_missing_knowledge(assessment.get("reason", ""), current_topic, track)
    missing_lines = "\n".join([f"- {item}" for item in missing]) or "- 当前信息不足，建议补充前置知识判断"
    return f"""请基于以下信息，写一份“超纲说明卡”。

【孩子实际年级】
{actual_grade}

【当前路线】
{TRACK_LABELS.get(track, track)}

【当前学习水平】
{learning_level}

【当前学习主题】
{current_topic or "未填写"}

【题目】
{question}

【学习水平边界】
{track_policy_text(track, learning_level)}

【知识点边界】
{topic_boundary_text(current_topic, track)}

【超纲原因】
{assessment.get("reason")}

【还没学到的关键知识】
{missing_lines}

【更适合的起点年级】
{assessment.get("suggested_grade", learning_level)}

请严格按照以下结构输出：

【结论】
状态：只能写“这题先别硬讲”
先抓：只写超出的关键点，不超过12个字
开口：只写家长现在更适合怎么说，不超过30个字

## 1. 这题为什么现在还讲不了
## 2. 不是孩子笨，而是还没学到哪里
## 3. 等孩子学会什么，这题就能开始解
## 4. 家长现在更适合怎么做

要求：
- 必须明确说“这题超出当前学习水平（{learning_level}）常规学习范围”
- 必须明确说“等孩子学会……”再接上前置知识
- 如果当前路线是“同年级拔高”，允许说明这是该路线之外的题，不要误说成普通同步超纲
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
            assessment = await assess_grade_fit(
                req.question,
                req.actual_grade,
                req.learning_level,
                req.current_topic,
                req.track,
            )

            if assessment.get("is_in_scope"):
                if req.correct_answer:
                    solution = f"答案（家长提供）：{req.correct_answer}"
                else:
                    solution = await r1_solve(req.question, req.learning_level)
                system_prompt = REPORT_PROMPT
                report_prompt = build_report_prompt(req, solution, assessment)
            else:
                system_prompt = OUT_OF_SCOPE_PROMPT
                report_prompt = build_out_of_scope_prompt(
                    req.actual_grade,
                    req.learning_level,
                    req.current_topic,
                    req.question,
                    assessment,
                    req.track,
                )

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


# ── 搭梯子 2.0 ──────────────────────────────────────────────

MOCK_DATA = {
    "success": True,
    "data": {
        "start_from": "先和孩子确认这道题最后要求什么，再引导他理解「6天完成」表示一天只完成一部分。",
        "stuck_points": [
            "孩子最容易卡在：不理解「6天完成」为什么能转成「一天完成多少」。",
            "也容易把「合作」误以为是把6和8直接相加。",
        ],
        "fallback_step": "如果孩子没懂「效率」，先退回去讲：整项工程看成一整块，一天只做其中的一部分。",
        "direct_script": "我们先不急着算答案。先看这题最后要求什么。想知道几天完成，就要先知道他们一天一共做多少，对不对？",
        "three_steps": {
            "say_it": "先让孩子说清：这题最后求什么，为什么第一步要先求一天完成多少。",
            "write_it": "让孩子写出甲一天完成1/6，乙一天完成1/8，再写合作一天完成多少。",
            "draw_it": "如果还是不懂，就把整项工程画成一条，再标出一天做的部分。",
        },
    },
}

V2_SYSTEM_PROMPT = """你是一个"小学生家长讲题急救助手"。

你的任务不是生成长篇解析，也不是只给答案，而是在家长输入一道小学数学题后，帮助家长立刻知道"这道题现在该怎么讲"。

请严格遵守：
- 输出对象首先是家长；
- 必须根据孩子当前年级决定讲法，不能调用高于该年级的背景知识；
- 不要长篇理论，不要像老师教案；
- 要短、准、能立刻用；
- 不要只给答案，要给"讲法"和"退路"；
- 优先解决"现在怎么办"，而不是追求面面俱到。

关于各字段的特别要求：

【stuck_points】
- 不要写"孩子可能不理解……"这种分析腔；
- 要写孩子实际会做出的错误动作或说出的错误话；
- 让家长一眼认出"对，我家孩子就是这样！"；
- 不要用"可能""也许"，直接说孩子会怎么做；
- 每条控制在30字以内。

【key_scripts】共三句，每句不超过40字：
- open：家长开口的第一句话，让孩子先确认一个最基础的事实，不要直接问算式；
- when_stuck：孩子卡住或答错时，家长立刻说的那句话，目的是退回更小的问题；
- verify：用来检验孩子是否真的听懂，让孩子自己说出关键步骤。

【wrong_answer_responses】1-2条，每条包含：
- child_says：孩子最典型的一种错误答法，直接引用孩子可能说的话；
- parent_says：家长听到这句话后，立刻该说的话——不要纠错，要引导回到上一个能答对的问题。

【parent_traps】2-3条，每条不超过25字：
- 写家长在讲这道题时最容易犯的具体错误说法或问法；
- 格式：直接写那句错误的话或行为，例如"连续反问孩子：那为什么？那然后呢？"；
- 不要写"不要……"这种说教句式，直接写那个行为本身。

请严格输出 JSON，不要输出额外解释，不要输出 markdown 代码块标记。
JSON 字段必须包含：
start_from,
stuck_points（数组，1-2条）,
fallback_step,
key_scripts: { open, when_stuck, verify },
wrong_answer_responses（数组，1-2条，每条含 child_says 和 parent_says）,
parent_traps（数组，2-3条）,
three_steps: { say_it, write_it, draw_it }"""


def build_v2_user_prompt(grade: str, question: str, student_answer: str, parent_note: str) -> str:
    return f"""请根据下面信息，生成这道题的"家长讲题方案"。

【孩子年级】
{grade}

【题目】
{question}

【孩子原答案（可选）】
{student_answer or "未填写"}

【家长补充说明（可选）】
{parent_note or "未填写"}

要求：
- 输出要适合小学生家长阅读；
- 不要写成长篇报告；
- 要让家长有"我现在知道怎么讲了"的感觉；
- 如果题目本身信息不足，请尽量指出并做最合理理解。"""


class GenerateV2Request(BaseModel):
    grade: str
    question: str
    student_answer: str = ""
    parent_note: str = ""
    model: str = ""  # "v3" or "r1"; empty means auto-select


# 判断题目难度的本地规则（不消耗 API）
COMPLEX_KEYWORDS = {
    "工程", "效率", "速度", "路程", "追及", "相遇", "分数", "比例", "百分",
    "利润", "折扣", "面积", "体积", "周长", "方程", "倍数", "公倍", "公因",
    "植树", "盈亏", "鸡兔", "年龄", "流水", "顺流", "逆流", "掉头", "往返",
    "循环", "规律", "等差", "数列", "排列", "组合", "概率",
}
HIGH_GRADES = {"四年级", "五年级", "六年级"}


def classify_complexity(grade: str, question: str) -> tuple[str, int]:
    """返回 (model, estimated_seconds)"""
    is_high_grade = grade in HIGH_GRADES
    is_long = len(question) > 60
    has_complex_keyword = any(kw in question for kw in COMPLEX_KEYWORDS)

    if is_high_grade and (is_long or has_complex_keyword):
        return "r1", 35
    if has_complex_keyword:
        return "r1", 30
    if is_high_grade and is_long:
        return "r1", 25
    return "v3", 8


@app.get("/v2", response_class=HTMLResponse)
async def index_v2(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})


@app.post("/api/v2/classify")
async def classify_v2(req: GenerateV2Request):
    """快速返回模型选择和预估时间，前端用于初始化进度条。"""
    model, estimated_seconds = classify_complexity(req.grade, req.question)
    return {"model": model, "estimated_seconds": estimated_seconds}


@app.post("/api/v2/generate")
async def generate_v2(req: GenerateV2Request):
    # Mock mode: if no API key configured, return mock data for UI testing
    if not DEEPSEEK_API_KEY:
        return MOCK_DATA

    # 选择模型：前端可传 model 字段，否则自动判断
    chosen_model, timeout_s = {
        "v3": ("deepseek-chat", 30),
        "r1": ("deepseek-reasoner", 120),
    }.get(req.model, ("deepseek-chat", 30))

    # 如果前端没传 model，用本地规则自动判断
    if not req.model:
        auto_model, _ = classify_complexity(req.grade, req.question)
        chosen_model, timeout_s = {
            "v3": ("deepseek-chat", 30),
            "r1": ("deepseek-reasoner", 120),
        }[auto_model]

    try:
        api_params: dict = {
            "model": chosen_model,
            "messages": [
                {"role": "system", "content": V2_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_v2_user_prompt(
                        req.grade, req.question, req.student_answer, req.parent_note
                    ),
                },
            ],
            "max_tokens": 2000 if chosen_model == "deepseek-chat" else 4000,
        }
        # deepseek-chat 支持 json_object 格式，R1 不支持
        if chosen_model == "deepseek-chat":
            api_params["response_format"] = {"type": "json_object"}
            api_params["temperature"] = 0.3

        async with httpx.AsyncClient(timeout=float(timeout_s)) as client:
            resp = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=api_params,
            )
        data = resp.json()
        raw_content = data["choices"][0]["message"]["content"]

        result = extract_json_object(raw_content)
        result.setdefault("start_from", "")
        result.setdefault("stuck_points", [])
        result.setdefault("fallback_step", "")
        result.setdefault("key_scripts", {"open": "", "when_stuck": "", "verify": ""})
        result.setdefault("wrong_answer_responses", [])
        result.setdefault("parent_traps", [])
        result.setdefault("three_steps", {"say_it": "", "write_it": "", "draw_it": ""})

        return {"success": True, "data": result}

    except Exception as e:
        return {"success": False, "error": f"生成失败，请稍后再试。({str(e)})"}
