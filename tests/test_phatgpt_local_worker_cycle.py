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
            with patch.object(worker, "ARTIFACT_ROOT", artifact_root):
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


if __name__ == "__main__":
    unittest.main()
