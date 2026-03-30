# 搭梯子品牌定位文案调整 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将“搭梯子”的首页与结果页文案统一到新定位：产品名保留“搭梯子”，首页主标题改为“顶级名师会这样讲”，副标题强调“一题讲透、家长照着讲也能讲得像样”。

**Architecture:** 本次只调整文案与提示词口径，不改题目判级、生成流程或结果结构。前端负责首页 hero、输入引导和结果页标题的展示更新；后端负责报告提示词中对产品定位的描述同步；测试覆盖首页文案与提示词口径，防止旧词“备课报告/解析/搜题”回流。

**Tech Stack:** FastAPI, Jinja2 template, vanilla JavaScript, Python unittest, Node.js assertion script

---

### Task 1: 更新首页品牌文案

**Files:**
- Modify: `/Users/yangming/datizi/templates/index.html`
- Test: `/Users/yangming/datizi/test_frontend_render.js`

- [ ] **Step 1: 先写前端失败用例，卡住首页旧文案**

```js
const fs = require('fs');
const assert = require('assert');

const html = fs.readFileSync('/Users/yangming/datizi/templates/index.html', 'utf8');

assert.ok(
  html.includes('顶级名师会这样讲'),
  'hero 标题必须改成“顶级名师会这样讲”'
);
assert.ok(
  html.includes('把一道题讲透，让家长照着讲也能讲得像样'),
  'hero 副标题必须强调“一题讲透”和“照着讲”'
);
assert.ok(
  !html.includes('帮小学生家长把题讲明白'),
  '旧 hero 文案不应继续保留'
);
```

- [ ] **Step 2: 运行前端用例，确认它先失败**

Run: `node /Users/yangming/datizi/test_frontend_render.js`  
Expected: FAIL，提示缺少新 hero 文案或仍含旧文案

- [ ] **Step 3: 修改首页 hero 和首屏输入区说明**

在 `/Users/yangming/datizi/templates/index.html` 中把以下文案替换为新定位：

```html
<h1>搭梯子</h1>
<p class="tagline">顶级名师会这样讲</p>
<p class="sub-tagline">把一道题讲透，让家长照着讲也能讲得像样</p>
```

并把输入区说明收口到“名师讲法 + 家长照着讲”：

```html
<p class="intro-main">不是再给你一份题解，而是先把名师讲这一题的路子给你</p>
<p class="intro-sub">把题贴进来，先看这题该抓什么、第一句怎么开口、孩子会卡在哪，家长照着讲也能更像样。</p>
```

- [ ] **Step 4: 重新运行前端用例，确认通过**

Run: `node /Users/yangming/datizi/test_frontend_render.js`  
Expected: PASS with `frontend render tests passed`

- [ ] **Step 5: 提交首页品牌文案改动**

```bash
git -C /Users/yangming/datizi add templates/index.html test_frontend_render.js
git -C /Users/yangming/datizi commit -m "feat: update homepage brand positioning copy"
```

### Task 2: 同步结果页文案口径

**Files:**
- Modify: `/Users/yangming/datizi/templates/index.html`
- Test: `/Users/yangming/datizi/test_frontend_render.js`

- [ ] **Step 1: 先写失败用例，卡住结果页旧口径**

在 `/Users/yangming/datizi/test_frontend_render.js` 追加断言：

```js
assert.ok(
  html.includes('这道题，顶级名师会这样讲'),
  '结果页标题应改成“这道题，顶级名师会这样讲”'
);
assert.ok(
  html.includes('先看结论、切入口和第一句开口，再决定你自己讲，还是让孩子顺着台阶理解。'),
  '结果页说明应改成新口径'
);
assert.ok(
  !html.includes('这道题，建议你先这样开口'),
  '旧结果页标题不应保留'
);
```

- [ ] **Step 2: 运行前端用例，确认失败**

Run: `node /Users/yangming/datizi/test_frontend_render.js`  
Expected: FAIL，提示结果页文案仍是旧版本

- [ ] **Step 3: 修改结果页标题与说明**

在 `/Users/yangming/datizi/templates/index.html` 中替换结果头部：

```html
<div class="result-header">
  <h2>这道题，顶级名师会这样讲</h2>
  <p>先看结论、切入口和第一句开口，再决定你自己讲，还是让孩子顺着台阶理解。</p>
</div>
```

如果有辅助提示文案，也统一避免“备课报告”“解析”等词，保持“讲透”“照着讲”的口径。

- [ ] **Step 4: 运行前端用例，确认通过**

Run: `node /Users/yangming/datizi/test_frontend_render.js`  
Expected: PASS with `frontend render tests passed`

- [ ] **Step 5: 提交结果页文案改动**

```bash
git -C /Users/yangming/datizi add templates/index.html test_frontend_render.js
git -C /Users/yangming/datizi commit -m "feat: align result page copy with brand positioning"
```

### Task 3: 同步后端提示词里的产品定位

**Files:**
- Modify: `/Users/yangming/datizi/main.py`
- Test: `/Users/yangming/datizi/test_main.py`

- [ ] **Step 1: 先写失败用例，防止后端 prompt 继续输出旧口径**

在 `/Users/yangming/datizi/test_main.py` 增加一个断言，验证 `build_report_prompt()` 和系统 prompt 不再强调“备课报告”，而是强调“名师讲法”和“讲透”：

```python
def test_build_report_prompt_uses_brand_positioning_language(self):
    req = main.GenerateRequest(
        actual_grade="四年级",
        learning_level="四年级",
        track="sync",
        question="题目",
        student_answer="",
        correct_answer="",
        parent_note="",
        current_topic="",
    )
    assessment = {
        "is_in_scope": True,
        "reason": "可解",
        "allowed_method": "数量关系",
        "forbidden_method": "方程",
    }
    prompt = main.build_report_prompt(req, "答案", assessment)
    self.assertIn("讲题副驾卡", prompt)
    self.assertIn("家长现在第一句该怎么说", prompt)
    self.assertNotIn("备课报告", prompt)
```

- [ ] **Step 2: 运行后端单测，确认先失败**

Run: `python3 -m unittest test_main.py`  
Expected: FAIL，提示 prompt 中仍存在旧文案或缺少新断言目标

- [ ] **Step 3: 修改后端提示词文案**

在 `/Users/yangming/datizi/main.py` 中收紧两处文案：

```python
REPORT_PROMPT = """你是“搭梯子”的家长讲题副驾。

你的任务不是生成题解，也不是写一份备课资料，而是把顶级名师讲这一题时会先抓什么、怎么开口、怎么层层讲透，翻成家长能直接照着用的讲法。
"""
```

并在 `build_report_prompt()` 的引导句里把“备课报告”类表达替换为：

```python
return f"""请基于以下信息生成一份“讲题副驾卡”。

目标不是再给一份解析，而是把这道题讲透，并让家长照着讲也能讲得像样。
"""
```

不要改结构字段，只改提示词里的定位话术。

- [ ] **Step 4: 运行后端测试和语法检查**

Run: `python3 -m unittest test_main.py`  
Expected: `OK`

Run: `python3 -m py_compile main.py`  
Expected: no output

- [ ] **Step 5: 提交后端文案口径改动**

```bash
git -C /Users/yangming/datizi add main.py test_main.py
git -C /Users/yangming/datizi commit -m "feat: align report prompts with brand positioning"
```

### Task 4: 最终回归与上线

**Files:**
- Verify: `/Users/yangming/datizi/templates/index.html`
- Verify: `/Users/yangming/datizi/main.py`
- Verify: `/Users/yangming/datizi/test_main.py`
- Verify: `/Users/yangming/datizi/test_frontend_render.js`

- [ ] **Step 1: 运行完整本地验证**

Run: `node /Users/yangming/datizi/test_frontend_render.js`  
Expected: `frontend render tests passed`

Run: `python3 -m unittest test_main.py`  
Expected: `OK`

Run: `python3 -m py_compile main.py`  
Expected: no output

- [ ] **Step 2: 人工检查关键文案落点**

打开以下位置，确认不再出现旧口径：

- 首页 hero：`搭梯子 / 顶级名师会这样讲 / 把一道题讲透，让家长照着讲也能讲得像样`
- 输入区说明：强调“名师讲法”“照着讲”
- 结果页标题：`这道题，顶级名师会这样讲`
- 结果结论卡：仍然保持“状态 / 先抓 / 开口”结构，不回退成摘要长文

- [ ] **Step 3: 提交最终整合提交**

```bash
git -C /Users/yangming/datizi add templates/index.html main.py test_main.py test_frontend_render.js
git -C /Users/yangming/datizi commit -m "feat: apply brand positioning copy across product"
```

- [ ] **Step 4: 推送上线**

```bash
git -C /Users/yangming/datizi push origin main
```

Expected: push 成功，Render 自动部署新版本

