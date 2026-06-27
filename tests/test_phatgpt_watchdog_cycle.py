import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import phatgpt_subagent_selector as selector
from scripts import phatgpt_watchdog_cycle as watchdog


class PhatgptWatchdogCycleTest(unittest.TestCase):
    def make_agent_root(self):
        tmp = TemporaryDirectory()
        root = Path(tmp.name)
        for agent_id in [
            "phatgpt-deployer",
            "phatgpt-reviewer",
            "phatgpt-coder",
            "phatgpt-researcher",
        ]:
            agent_dir = root / agent_id
            agent_dir.mkdir()
            agent_dir.joinpath("AGENTS.md").write_text(
                f"---\nid: {agent_id}\ntitle: {agent_id}\nkind: worker\n---\n# {agent_id}\n",
                encoding="utf-8",
            )
        return tmp, root

    def test_lane_priority_selects_deployer_before_reviewer(self):
        tmp, root = self.make_agent_root()
        self.addCleanup(tmp.cleanup)
        lanes = selector.build_lanes(root)
        self.assertGreaterEqual(len(lanes), 4)
        self.assertEqual(lanes[0]["name"], "deployer")
        self.assertEqual(lanes[1]["name"], "reviewer")
        self.assertEqual(lanes[2]["name"], "coder")

    def test_researcher_scans_issue_before_pr(self):
        tmp, root = self.make_agent_root()
        self.addCleanup(tmp.cleanup)
        names = [lane["name"] for lane in selector.build_lanes(root)]
        self.assertLess(names.index("researcher-issue"), names.index("researcher-pr"))

    def test_lane_commands_delegate_to_existing_workers(self):
        tmp, root = self.make_agent_root()
        self.addCleanup(tmp.cleanup)
        commands = [" ".join(lane["command"]) for lane in selector.build_lanes(root)]
        self.assertTrue(any("scripts/phatgpt_deployer_cycle.py" in command for command in commands))
        self.assertTrue(any("scripts/phatgpt_local_worker_cycle.py" in command for command in commands))

    def test_lanes_are_sourced_from_agent_contracts(self):
        tmp, root = self.make_agent_root()
        self.addCleanup(tmp.cleanup)
        lanes = selector.build_lanes(root)
        self.assertTrue(all(lane["selector_source"] == "agent-skills/agents" for lane in lanes))
        self.assertTrue(all(lane["contract_path"].endswith("AGENTS.md") for lane in lanes))

    def test_task_recommendation_prefers_coder_for_mutation(self):
        recommendation = selector.recommend_subagent("Implement a bounded code change.")
        self.assertEqual(recommendation["recommended_subagent"], "phatgpt-coder")

    def test_task_recommendation_prefers_reviewer_for_validation(self):
        recommendation = selector.recommend_subagent("Review and validate the PR evidence.")
        self.assertEqual(recommendation["recommended_subagent"], "phatgpt-reviewer")

    def test_task_recommendation_defaults_ambiguous_to_researcher(self):
        recommendation = selector.recommend_subagent("Figure out what the next task should be.")
        self.assertEqual(recommendation["recommended_subagent"], "phatgpt-researcher")

    def test_task_recommendation_routes_mixed_roles_to_researcher(self):
        recommendation = selector.recommend_subagent("Implement a patch and review it for PASS.")
        self.assertEqual(recommendation["recommended_subagent"], "phatgpt-researcher")
        self.assertEqual(recommendation["reason"], "ambiguous_multi_role_task_requires_researcher_refusal_or_task_split")

    def test_task_recommendation_includes_matched_intents(self):
        recommendation = selector.recommend_subagent("Validate the deployment proof.")
        self.assertIn("phatgpt-deployer", recommendation["matched_intents"])
        self.assertIn("phatgpt-reviewer", recommendation["matched_intents"])
        self.assertEqual(recommendation["recommended_subagent"], "phatgpt-researcher")

    def test_compact_memory_item_truncates_large_fields(self):
        compact = selector.compact_memory_item(
            {
                "_key": "k",
                "_source": "lessons",
                "problem": "p" * 500,
                "solution": "s" * 500,
                "tags": list("abcdefghijk"),
                "scores": {"bm25": 1.0, "dense": 0.5, "extra": "drop"},
            }
        )
        self.assertEqual(len(compact["problem"]), 300)
        self.assertEqual(len(compact["solution"]), 300)
        self.assertEqual(len(compact["tags"]), 8)
        self.assertNotIn("extra", compact["scores"])

    def test_format_command_substitutes_repo_and_label(self):
        command = watchdog.format_command(["--repo", "{repo}", "--label", "{label}"], "owner/repo", "ready")
        self.assertEqual(command, ["--repo", "owner/repo", "--label", "ready"])

    def test_load_stale_targets_normalizes_pull_request(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.json"
            path.write_text(
                '{"stale_or_superseded_items":[{"kind":"pull_request","number":8},{"kind":"issue","number":11}]}',
                encoding="utf-8",
            )
            self.assertEqual(watchdog.load_stale_targets(path), {("pr", 8), ("issue", 11)})

    def test_target_is_available_rejects_stale_active_or_assigned(self):
        self.assertFalse(watchdog.target_is_available("pr", 8, {"labels": [], "assignees": []}, {("pr", 8)}))
        self.assertFalse(
            watchdog.target_is_available(
                "pr",
                9,
                {"labels": [{"name": "maintainer-active"}], "assignees": []},
                set(),
            )
        )
        self.assertFalse(
            watchdog.target_is_available(
                "issue",
                10,
                {"labels": [], "assignees": [{"login": "grahama1970"}]},
                set(),
            )
        )
        self.assertTrue(watchdog.target_is_available("issue", 12, {"labels": [], "assignees": []}, set()))


if __name__ == "__main__":
    unittest.main()
