import unittest

from scripts import phatgpt_deployer_cycle as deployer
from scripts import phatgpt_review_deployer_receipt as reviewer


def pr_fixture(*, merge_state="CLEAN", check_conclusion="SUCCESS"):
    return {
        "state": "OPEN",
        "isDraft": False,
        "labels": [
            {"name": "phatgpt-ready-to-deploy"},
            {"name": "phatgpt-pass"},
        ],
        "mergeStateStatus": merge_state,
        "reviewDecision": "",
        "comments": [
            {"body": "PhatGPT reviewer receipt\n\n- reason: `review_pass`"}
        ],
        "statusCheckRollup": [
            {"name": "validate-control-plane", "conclusion": check_conclusion},
            {"name": "Benchmark evidence", "conclusion": "SUCCESS"},
            {"name": "Build Pages artifact", "conclusion": "SUCCESS"},
            {"name": "phatgpt-opencode", "status": "IN_PROGRESS"},
        ],
        "headRefOid": "abc123",
        "headRefName": "sanity",
        "baseRefName": "main",
    }


class PhatgptDeployerCycleTest(unittest.TestCase):
    def test_deployer_allows_unstable_when_required_checks_pass(self):
        status, missing, summary = deployer.evaluate_pr(
            pr_fixture(merge_state="UNSTABLE"),
            ["validate-control-plane", "Benchmark evidence", "Build Pages artifact"],
        )

        self.assertEqual(status, "WOULD_MERGE")
        self.assertEqual(missing, [])
        self.assertEqual(summary["merge_state"], "UNSTABLE")

    def test_deployer_rejects_missing_required_check_even_when_unstable_is_allowed(self):
        status, missing, _summary = deployer.evaluate_pr(
            pr_fixture(merge_state="UNSTABLE", check_conclusion=""),
            ["validate-control-plane", "Benchmark evidence", "Build Pages artifact"],
        )

        self.assertEqual(status, "REFUSED")
        self.assertIn("check_success:validate-control-plane", missing)

    def test_deployer_receipt_reviewer_accepts_unstable_with_green_required_checks(self):
        receipt = {
            "schema": "chatgpt_lab.deployer_receipt.v1",
            "role": "deployer",
            "dry_run": True,
            "status": "WOULD_MERGE",
            "missing": [],
            "gate_summary": {
                "reviewer_pass_comment": True,
                "merge_state": "UNSTABLE",
                "acceptable_merge_states": ["CLEAN", "HAS_HOOKS", "UNSTABLE"],
                "required_checks": {
                    "validate-control-plane": "SUCCESS",
                    "Benchmark evidence": "SUCCESS",
                    "Build Pages artifact": "SUCCESS",
                },
            },
        }

        verdict, reason, findings = reviewer.review_receipt(receipt)

        self.assertEqual(verdict, "PASS")
        self.assertEqual(reason, "deployer_receipt_approved")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
