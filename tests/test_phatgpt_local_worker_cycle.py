import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import phatgpt_local_worker_cycle as worker


class PhatgptLocalWorkerCycleTest(unittest.TestCase):
    def test_researcher_refuses_inventory_task_without_inventory_output(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json"],
            "expected_evidence": [
                "capability inventory covers F36 plant, Embry OS, pdf-lab, SPARTA/QRA, Lean4, graph-memory, watch, and agent-skills"
            ],
        }

        status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
            task,
            commands_run,
            kind="issue",
            number=18,
        )

        self.assertEqual(status, "REFUSED")
        self.assertEqual(reason, "researcher_evidence_missing")
        self.assertIn("capability_inventory_artifact", missing)
        self.assertEqual(files_touched, [])
        self.assertIn("before coder routing", next_required_action)

    def test_researcher_refuses_inventory_task_when_declared_output_is_missing_on_disk(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json", "capability-inventory.json"],
            "expected_evidence": [
                "capability inventory covers F36 plant, Embry OS, pdf-lab, SPARTA/QRA, Lean4, graph-memory, watch, and agent-skills"
            ],
        }

        with TemporaryDirectory() as tmp, patch.object(worker, "ARTIFACT_ROOT", Path(tmp)), patch.object(worker, "collect_capability_inventory", side_effect=RuntimeError("collector unavailable")):
            status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
                task,
                commands_run,
                kind="issue",
                number=18,
            )

        self.assertEqual(status, "REFUSED")
        self.assertEqual(reason, "researcher_evidence_missing")
        self.assertIn("capability_inventory_artifact_missing", missing)
        self.assertEqual(files_touched, [])
        self.assertIn("before coder routing", next_required_action)

    def test_researcher_collects_missing_inventory_artifact(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json", "capability-inventory.json"],
            "expected_evidence": [
                "capability inventory covers F36 plant, Embry OS, pdf-lab, SPARTA/QRA, Lean4, graph-memory, watch, and agent-skills"
            ],
        }

        with TemporaryDirectory() as tmp:
            artifact_root = Path(tmp)
            def fake_collect(_root, out_root, kind, number):
                out_dir = out_root / f"{kind}-{number}"
                out_dir.mkdir(parents=True, exist_ok=True)
                path = out_dir / "capability-inventory.json"
                path.write_text("{}\n", encoding="utf-8")
                return path, [{"command": "fake_collect_capability_inventory", "exit_code": 0}]

            with patch.object(worker, "ARTIFACT_ROOT", artifact_root), patch.object(worker, "collect_capability_inventory", side_effect=fake_collect):
                status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
                    task,
                    commands_run,
                    kind="issue",
                    number=18,
                )

        self.assertEqual(status, "COMPLETED")
        self.assertEqual(reason, "researcher_evidence_collected")
        self.assertEqual(missing, [])
        self.assertEqual(files_touched, [])
        self.assertIn("researcher evidence", next_required_action)

    def test_researcher_completes_only_when_inventory_artifact_exists(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json", "capability-inventory.json"],
            "expected_evidence": [
                "capability inventory covers F36 plant, Embry OS, pdf-lab, SPARTA/QRA, Lean4, graph-memory, watch, and agent-skills"
            ],
        }

        with TemporaryDirectory() as tmp:
            artifact_root = Path(tmp)
            inventory_dir = artifact_root / "issue-18"
            inventory_dir.mkdir()
            inventory_dir.joinpath("capability-inventory.json").write_text("{}\n", encoding="utf-8")
            with patch.object(worker, "ARTIFACT_ROOT", artifact_root), patch.object(worker, "collect_capability_inventory") as collect:
                status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
                    task,
                    commands_run,
                    kind="issue",
                    number=18,
                )

        collect.assert_not_called()
        self.assertEqual(status, "COMPLETED")
        self.assertEqual(reason, "researcher_evidence_collected")
        self.assertEqual(missing, [])
        self.assertEqual(files_touched, [])
        self.assertIn("researcher evidence", next_required_action)

    def test_researcher_refuses_stress_plan_task_without_declared_output(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json"],
            "expected_evidence": [
                "stress-test plan for Embry OS / SPARTA Explorer greenfield loop"
            ],
        }

        status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
            task,
            commands_run,
            kind="issue",
            number=20,
        )

        self.assertEqual(status, "REFUSED")
        self.assertEqual(reason, "researcher_evidence_missing")
        self.assertIn("stress_test_plan_artifact", missing)
        self.assertEqual(files_touched, [])
        self.assertIn("before coder routing", next_required_action)

    def test_researcher_collects_missing_stress_plan_artifact(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json", "stress-test-plan.json"],
            "expected_evidence": [
                "stress-test plan for Embry OS / SPARTA Explorer greenfield loop"
            ],
        }

        with TemporaryDirectory() as tmp:
            artifact_root = Path(tmp)

            def fake_collect(_root, out_root, kind, number):
                out_dir = out_root / f"{kind}-{number}"
                out_dir.mkdir(parents=True, exist_ok=True)
                path = out_dir / "stress-test-plan.json"
                path.write_text("{}\n", encoding="utf-8")
                return path, [{"command": "fake_collect_stress_test_plan", "exit_code": 0}]

            with patch.object(worker, "ARTIFACT_ROOT", artifact_root), patch.object(worker, "collect_stress_test_plan", side_effect=fake_collect):
                status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
                    task,
                    commands_run,
                    kind="issue",
                    number=20,
                )

        self.assertEqual(status, "COMPLETED")
        self.assertEqual(reason, "researcher_evidence_collected")
        self.assertEqual(missing, [])
        self.assertEqual(files_touched, [])
        self.assertIn("researcher evidence", next_required_action)

    def test_researcher_completes_only_when_stress_plan_artifact_exists(self):
        commands_run = []
        task = {
            "allowed_commands": ["python3 -c pass"],
            "validation_commands": ["python3 -c pass"],
            "required_outputs": ["local-subagent-receipt.json", "stress-test-plan.json"],
            "expected_evidence": [
                "stress-test plan for Embry OS / SPARTA Explorer greenfield loop"
            ],
        }

        with TemporaryDirectory() as tmp:
            artifact_root = Path(tmp)
            plan_dir = artifact_root / "issue-20"
            plan_dir.mkdir()
            plan_dir.joinpath("stress-test-plan.json").write_text("{}\n", encoding="utf-8")
            with patch.object(worker, "ARTIFACT_ROOT", artifact_root), patch.object(worker, "collect_stress_test_plan") as collect:
                status, reason, missing, files_touched, next_required_action = worker.execute_researcher_task(
                    task,
                    commands_run,
                    kind="issue",
                    number=20,
                )

        collect.assert_not_called()
        self.assertEqual(status, "COMPLETED")
        self.assertEqual(reason, "researcher_evidence_collected")
        self.assertEqual(missing, [])
        self.assertEqual(files_touched, [])
        self.assertIn("researcher evidence", next_required_action)

    def test_write_receipt_preserves_role_specific_receipts_and_latest_alias(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_root = root / "artifacts" / "local-worker"
            with patch.object(worker, "ROOT", root), patch.object(worker, "ARTIFACT_ROOT", artifact_root):
                coder_receipt = worker.write_receipt(
                    role="coder",
                    kind="pr",
                    number=19,
                    task_id="sanity-001",
                    status="COMPLETED",
                    reason="task_executed_and_pushed",
                    missing=[],
                    next_required_action="Reviewer should inspect this PR.",
                    commands_run=[],
                    target=None,
                )
                reviewer_receipt = worker.write_receipt(
                    role="reviewer",
                    kind="pr",
                    number=19,
                    task_id="sanity-001",
                    status="COMPLETED",
                    reason="review_pass",
                    missing=[],
                    next_required_action="Deployer should check release gates.",
                    commands_run=[],
                    target=None,
                )

            latest_receipt = artifact_root / "pr-19" / "local-subagent-receipt.json"
            coder_data = coder_receipt.read_text(encoding="utf-8")
            reviewer_data = reviewer_receipt.read_text(encoding="utf-8")
            latest_data = latest_receipt.read_text(encoding="utf-8")

        self.assertEqual(coder_receipt.name, "coder-local-subagent-receipt.json")
        self.assertEqual(reviewer_receipt.name, "reviewer-local-subagent-receipt.json")
        self.assertIn('"role": "coder"', coder_data)
        self.assertIn('"reason": "task_executed_and_pushed"', coder_data)
        self.assertIn('"role": "reviewer"', reviewer_data)
        self.assertIn('"reason": "review_pass"', reviewer_data)
        self.assertIn('"role": "reviewer"', latest_data)
        self.assertIn("reviewer-local-subagent-receipt.json", latest_data)

    def test_write_receipt_includes_existing_sidecar_json_artifacts(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_root = root / "artifacts" / "local-worker"
            sidecar_dir = artifact_root / "issue-20"
            sidecar_dir.mkdir(parents=True)
            sidecar_dir.joinpath("stress-test-plan.json").write_text("{}\n", encoding="utf-8")
            with patch.object(worker, "ROOT", root), patch.object(worker, "ARTIFACT_ROOT", artifact_root):
                receipt_path = worker.write_receipt(
                    role="researcher",
                    kind="issue",
                    number=20,
                    task_id="stress-001",
                    status="COMPLETED",
                    reason="researcher_evidence_collected",
                    missing=[],
                    next_required_action="WebGPT may use the researcher evidence.",
                    commands_run=[],
                    target=None,
                )

            receipt = receipt_path.read_text(encoding="utf-8")

        self.assertIn("artifacts/local-worker/issue-20/stress-test-plan.json", receipt)


if __name__ == "__main__":
    unittest.main()
