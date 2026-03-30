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

import curriculum_rules
import main


class MainHelpersTest(unittest.TestCase):
    def test_grade_policy_mentions_allowed_and_forbidden_methods(self):
        policy = main.grade_policy_text("四年级")
        self.assertIn("只允许使用四年级及以下", policy)
        self.assertIn("数量关系", policy)
        self.assertIn("不得使用方程", policy)
        self.assertIn("不得一上来设x、y", policy)

    def test_out_of_scope_prompt_mentions_next_knowledge(self):
        prompt = main.build_out_of_scope_prompt(
            actual_grade="一年级",
            learning_level="一年级",
            current_topic="简易方程",
            question="一个稍复杂的方程题",
            assessment={
                "is_in_scope": False,
                "reason": "需要简易方程",
                "missing_knowledge": ["用字母表示未知数", "根据等量关系列方程"],
                "suggested_grade": "五年级",
                "allowed_method": "",
            },
        )
        self.assertIn("超出当前学习水平（一年级）常规学习范围", prompt)
        self.assertIn("等孩子学会", prompt)
        self.assertIn("用字母表示未知数", prompt)
        self.assertIn("五年级", prompt)
        self.assertIn("当前学习主题", prompt)

    def test_sanitize_report_text_removes_latex_markers(self):
        raw = r"公式是 [ \frac{x+15}{x+y+15} = \frac{1}{3} ]，且 y = 2x + 30 \quad (1)"
        cleaned = main.sanitize_report_text(raw)
        self.assertNotIn(r"\frac", cleaned)
        self.assertNotIn(r"\quad", cleaned)
        self.assertNotIn("[", cleaned)
        self.assertIn("(x+15)/(x+y+15) = (1)/(3)", cleaned)

    def test_build_report_prompt_uses_learning_level_not_actual_grade(self):
        req = main.GenerateRequest(
            actual_grade="三年级",
            learning_level="六年级",
            question="测试题",
            student_answer="",
            correct_answer="",
            parent_note="",
            current_topic="比和比例",
        )
        prompt = main.build_report_prompt(req, "答案略", {
            "is_in_scope": True,
            "reason": "按当前学习水平可解",
            "allowed_method": "按六年级方法讲",
            "forbidden_method": "不要跨到初中",
        })
        self.assertIn("孩子实际年级", prompt)
        self.assertIn("三年级", prompt)
        self.assertIn("当前学习水平", prompt)
        self.assertIn("六年级", prompt)

    def test_topic_boundary_normalizes_alias(self):
        topic = curriculum_rules.normalize_topic_name("孩子最近在学比和比例")
        self.assertEqual(topic, "比和比例")

    def test_topic_boundary_text_mentions_prerequisites(self):
        text = curriculum_rules.topic_boundary_text("简易方程")
        self.assertIn("五年级", text)
        self.assertIn("用字母表示未知数", text)

    def test_infer_missing_knowledge_prefers_current_topic(self):
        missing = curriculum_rules.infer_missing_knowledge("原因随便", "简易方程")
        self.assertIn("用字母表示未知数", missing)
        self.assertIn("等量关系", missing)


if __name__ == "__main__":
    unittest.main()
