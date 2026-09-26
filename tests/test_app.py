"""Regression checks for request handling, response validation, and data storage.

Run with: python -m unittest discover -s tests -v
No external LLM calls are made.
"""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("plaque_app", ROOT / "app.py")
module = importlib.util.module_from_spec(spec)
# Use dummy complete settings so a developer's local credentials are never loaded.
with patch.dict(os.environ, {
    "API_KEY": "test-placeholder",
    "API_BASE_URL": "http://127.0.0.1:1/v1",
    "API_MODEL": "test-model",
    "API_MAX_TOKENS": "4096",
    "API_TEMPERATURE": "0.1",
    "API_NO_THINK": "false",
    "ENABLE_EVALUATION_STORAGE": "false",
}):
    spec.loader.exec_module(module)
module.CLIENT.close()
module.CLIENT = None


class AppTests(unittest.TestCase):
    def setUp(self):
        module.app.config.update(TESTING=True, ENABLE_EVALUATION_STORAGE=False)
        self.client = module.app.test_client()

    def test_examples_and_invalid_language(self):
        for lang in ("zh", "en"):
            result = self.client.get(f"/api/examples?lang={lang}")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(len(result.json["examples"]), 5)
            self.assertEqual(self.client.get(f"/api/examples/case_001?lang={lang}").status_code, 200)
        for url in ("/api/examples?lang=unknown", "/api/examples/case_001?lang=unknown"):
            self.assertEqual(self.client.get(url).status_code, 400)
        self.assertEqual(self.client.get("/api/examples/missing").status_code, 404)

    def test_inference_rejects_malformed_requests_before_api_call(self):
        payloads = [[], None, "text", {}, {"findings": 5}, {"findings": []},
                    {"findings": "carotid", "language": []},
                    {"findings": "carotid", "prompt_version": {}},
                    {"findings": "x" * 20001}]
        api = Mock()
        with patch.object(module, "CLIENT", api):
            for payload in payloads:
                with self.subTest(payload_type=type(payload).__name__):
                    self.assertEqual(self.client.post("/api/infer", json=payload).status_code, 400)
            api.chat.completions.create.assert_not_called()
        result = self.client.post("/api/infer", json={"findings": "carotid plaque", "language": "en"})
        self.assertEqual(result.status_code, 503)

    def test_request_size_limit(self):
        result = self.client.post("/api/infer", json={"findings": "a" * (129 * 1024)})
        self.assertEqual(result.status_code, 413)

    def test_inference_success_and_optional_provider_directive(self):
        answers = {
            "en": {"Reasoning Process": "Example explanation", "AHA Classification": {"Left": "IV-V", "Right": "VII"}},
            "zh": {"推理过程": "示例解释", "AHA分型": {"左侧": "IV-V", "右侧": "VII"}},
        }
        for lang, answer in answers.items():
            for version in ("NP", "CGP"):
                api = Mock()
                api.chat.completions.create.return_value = SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(answer)))])
                with patch.object(module, "CLIENT", api), patch.object(module, "NO_THINK", False):
                    result = self.client.post("/api/infer", json={
                        "findings": "MRI carotid plaque", "language": lang, "prompt_version": version})
                self.assertEqual(result.status_code, 200)
                self.assertTrue(result.json["validated"])
                self.assertEqual(result.json["data"], answer)
                prompt = api.chat.completions.create.call_args.kwargs["messages"][0]["content"]
                self.assertTrue(prompt.startswith(module.PROMPTS[version][lang]))
                self.assertNotIn("/no_think", prompt)
        with patch.object(module, "CLIENT", api), patch.object(module, "NO_THINK", True):
            self.client.post("/api/infer", json={"findings": "MRI carotid plaque"})
        self.assertTrue(api.chat.completions.create.call_args.kwargs["messages"][0]["content"].endswith(" /no_think"))

    def test_schema_failures_never_marked_valid_or_logged_with_input(self):
        for raw in (None, "", "[]", "null", "42", "{}", '{"Reasoning Process":"secret-report-marker"}',
                    '{"Reasoning Process":{},"AHA Classification":{"Left":"VI"}}',
                    '{"Reasoning Process":"","AHA Classification":{"Left":"","Right":""}}'):
            for lang in ("zh", "en"):
                result = module.validate_and_parse_ai_response(raw, lang)
                self.assertFalse(result["success"])
                self.assertNotIn("secret-report-marker", result["error"])
        with self.assertLogs(module.logger, level="WARNING") as logs:
            module.validate_and_parse_ai_response('{"Reasoning Process":"secret-report-marker"}', "en")
        self.assertNotIn("secret-report-marker", " ".join(logs.output))
        valid = {"Reasoning Process": "Explanation", "AHA Classification": {"Left": "VI", "Right": "None"}}
        fenced = "```json\n" + json.dumps(valid) + "\n```"
        self.assertTrue(module.validate_and_parse_ai_response(fenced, "en")["success"])

    def test_api_errors_do_not_leak_credentials_or_reports(self):
        api = Mock()
        api.chat.completions.create.side_effect = RuntimeError("private-key-and-report-marker")
        with patch.object(module, "CLIENT", api), self.assertLogs(module.logger, level="ERROR") as logs:
            result = self.client.post("/api/infer", json={"findings": "carotid plaque", "language": "en"})
        self.assertEqual(result.status_code, 502)
        self.assertNotIn("private-key-and-report-marker", result.get_data(as_text=True))
        self.assertNotIn("private-key-and-report-marker", " ".join(logs.output))

    def test_no_cross_origin_api_access(self):
        result = self.client.get("/api/examples", headers={"Origin": "https://example.invalid"})
        self.assertNotIn("Access-Control-Allow-Origin", result.headers)

    def test_evaluation_is_opt_in_and_rejects_path_traversal(self):
        payload = {
            "username": "local_user_test", "findings": "carotid plaque", "ai_result": "example output",
            "labels": {"left_assessment": "I-II", "right_assessment": "VI", "left_usefulness": 1, "right_usefulness": 5},
        }
        with tempfile.TemporaryDirectory() as directory, patch.object(module, "USER_DATA_PATH", directory):
            self.assertFalse(self.client.get("/api/settings").json["evaluation_storage_enabled"])
            self.assertEqual(self.client.post("/api/custom/submit", json=payload).status_code, 403)
            self.assertEqual(list(Path(directory).iterdir()), [])
            module.app.config["ENABLE_EVALUATION_STORAGE"] = True
            for username in ("../escape", "/absolute", "a/b", "a\\b", "a" * 65, None, []):
                self.assertEqual(self.client.post("/api/custom/submit", json={**payload, "username": username}).status_code, 400)
            for override in ({"labels": []}, {"findings": 2}, {"ai_result": {}}, {"labels": {}}):
                self.assertEqual(self.client.post("/api/custom/submit", json={**payload, **override}).status_code, 400)
            for invalid in ({"left_assessment": "I"}, {"left_usefulness": True}, {"right_usefulness": 6}):
                bad = {**payload, "labels": {**payload["labels"], **invalid}}
                self.assertEqual(self.client.post("/api/custom/submit", json=bad).status_code, 400)
            self.assertEqual(list(Path(directory).iterdir()), [])
            first = self.client.post("/api/custom/submit", json=payload)
            second = self.client.post("/api/custom/submit", json=payload)
            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 200)
            self.assertNotEqual(first.json["custom_id"], second.json["custom_id"])
            files = list(Path(directory).glob("*.json"))
            self.assertEqual(len(files), 2)
            for path in files:
                self.assertEqual(json.loads(path.read_text())["findings"], payload["findings"])
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
