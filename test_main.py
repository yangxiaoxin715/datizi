import sys
import types
import unittest


def _stub_modules():
    httpx = types.ModuleType("httpx")
    httpx.AsyncClient = object
    sys.modules.setdefault("httpx", httpx)

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda: None
    sys.modules.setdefault("dotenv", dotenv)

    fastapi = types.ModuleType("fastapi")
    class FakeFastAPI:
        def mount(self, *args, **kwargs):
            return None
        def get(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
        def post(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
    fastapi.FastAPI = FakeFastAPI
    fastapi.Request = object
    sys.modules.setdefault("fastapi", fastapi)

    responses = types.ModuleType("fastapi.responses")
    class HTMLResponse:
        def __init__(self, *args, **kwargs):
            pass
    class StreamingResponse:
        def __init__(self, *args, **kwargs):
            pass
    responses.HTMLResponse = HTMLResponse
    responses.StreamingResponse = StreamingResponse
    sys.modules.setdefault("fastapi.responses", responses)

    staticfiles = types.ModuleType("fastapi.staticfiles")
    class StaticFiles:
        def __init__(self, *args, **kwargs):
            pass
    staticfiles.StaticFiles = StaticFiles
    sys.modules.setdefault("fastapi.staticfiles", staticfiles)

    templating = types.ModuleType("fastapi.templating")
    class FakeTemplates:
        def __init__(self, *args, **kwargs):
            pass
        def TemplateResponse(self, *args, **kwargs):
            return None
    templating.Jinja2Templates = FakeTemplates
    sys.modules.setdefault("fastapi.templating", templating)

    pydantic = types.ModuleType("pydantic")
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    pydantic.BaseModel = BaseModel
    sys.modules.setdefault("pydantic", pydantic)


_stub_modules()

import main


class MainHelpersTest(unittest.TestCase):
    def test_grade_policy_mentions_allowed_and_forbidden_methods(self):
        policy = main.grade_policy_text("四年级")
        self.assertIn("只允许使用四年级及以下", policy)
        self.assertIn("数量关系", policy)
        self.assertIn("不得使用方程", policy)

    def test_out_of_scope_prompt_mentions_next_knowledge(self):
        prompt = main.build_out_of_scope_prompt(
            grade="一年级",
            question="一个稍复杂的方程题",
            assessment={
                "is_in_scope": False,
                "reason": "需要简易方程",
                "missing_knowledge": ["用字母表示未知数", "根据等量关系列方程"],
                "suggested_grade": "五年级",
                "allowed_method": "",
            },
        )
        self.assertIn("超出一年级常规学习范围", prompt)
        self.assertIn("等孩子学会", prompt)
        self.assertIn("用字母表示未知数", prompt)
        self.assertIn("五年级", prompt)

    def test_sanitize_report_text_removes_latex_markers(self):
        raw = r"公式是 [ \frac{x+15}{x+y+15} = \frac{1}{3} ]，且 y = 2x + 30 \quad (1)"
        cleaned = main.sanitize_report_text(raw)
        self.assertNotIn(r"\frac", cleaned)
        self.assertNotIn(r"\quad", cleaned)
        self.assertNotIn("[", cleaned)
        self.assertIn("(x+15)/(x+y+15) = (1)/(3)", cleaned)


if __name__ == "__main__":
    unittest.main()
