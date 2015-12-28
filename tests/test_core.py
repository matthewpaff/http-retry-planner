from pathlib import Path
import unittest

from retries_lab.core import plan_retry
from retries_lab.fixture_check import check


class RetryTests(unittest.TestCase):
    def test_backoff_cap_and_server_minimum(self):
        self.assertEqual(plan_retry({"status": 503, "attempt": 3, "base_seconds": 10, "cap_seconds": 20})["delay_seconds"], 20)
        self.assertEqual(plan_retry({"status": 429, "retry_after": 120, "cap_seconds": 20})["delay_seconds"], 120)

    def test_method_and_attempt_limits(self):
        self.assertEqual(plan_retry({"status": 503, "method": "POST"})["reason"], "unsafe_method")
        self.assertTrue(plan_retry({"status": 503, "method": "POST", "idempotent": True})["retry"])
        self.assertEqual(plan_retry({"status": 503, "attempt": 4})["reason"], "attempt_limit")
        self.assertFalse(plan_retry({"status": 200})["retry"])

    def test_connection_errors_and_validation(self):
        self.assertTrue(plan_retry({"status": None})["retry"])
        for data in ({"status": True}, {"status": 503, "attempt": 0}, {"status": 503, "idempotent": 1}):
            with self.assertRaises(ValueError):
                plan_retry(data)

    def test_complete_fixture_corpus(self):
        self.assertGreaterEqual(check(Path(__file__).resolve().parents[1] / "fixtures/cases.jsonl", plan_retry), 350)


if __name__ == "__main__":
    unittest.main()
