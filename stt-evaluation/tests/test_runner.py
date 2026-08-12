import json
import tempfile
import unittest
from pathlib import Path

import run_eval


class RunnerTests(unittest.TestCase):
    def test_score(self):
        case = {"must_include": ["QA"], "forbidden": ["완료"]}
        self.assertTrue(run_eval.score(case, "QA 빌드 검토" )["semantic_valid"])
        self.assertFalse(run_eval.score(case, "QA 완료")["semantic_valid"])

    def test_load_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(json.dumps({"case_id": "x", "audio": "x.wav"}) + "\n", encoding="utf-8")
            self.assertEqual(len(run_eval.load_cases(path)), 1)


if __name__ == "__main__":
    unittest.main()
