#!/usr/bin/env python3
"""Tests for no-mutation GitHub-state orchestrator dry-run."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_ticket_orchestrator import github_json_to_thread_fixture, load_json, route_thread


class AgentTicketOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.goal = load_json(ROOT / "goals/current.json")

    def test_saved_pr_github_state_detects_legacy_without_mutation(self) -> None:
        data = load_json(ROOT / "examples/agent-harness/github-state/pr-13-gh-view.json")
        fixture = github_json_to_thread_fixture("pr", data)
        decision = route_thread(fixture, self.goal, {"grahama1970"})
        self.assertEqual("REFUSED", decision["status"])
        self.assertEqual(
            "legacy_phatgpt_task_detected_but_not_routable_in_this_slice",
            decision["reason"],
        )
        self.assertFalse(decision["would_mutate"])
        self.assertFalse(decision["orchestrator"]["would_mutate"])

    def test_github_json_to_thread_fixture_preserves_comments(self) -> None:
        data = load_json(ROOT / "examples/agent-harness/github-state/pr-13-gh-view.json")
        fixture = github_json_to_thread_fixture("pr", data)
        self.assertEqual("chatgpt_lab.github_thread_fixture.v1", fixture["schema"])
        self.assertEqual("pr", fixture["kind"])
        self.assertEqual(13, fixture["number"])
        self.assertEqual("grahama1970", fixture["author"])
        self.assertEqual(1, len(fixture["comments"]))
        self.assertEqual("github-actions", fixture["comments"][0]["author"])

    def test_saved_issue_github_state_routes_tau_handoff_without_mutation(self) -> None:
        data = load_json(ROOT / "examples/agent-harness/github-state/issue-14-tau-comment-gh-view.json")
        fixture = github_json_to_thread_fixture("issue", data)
        decision = route_thread(fixture, self.goal, {"grahama1970"})
        self.assertEqual("ROUTE", decision["status"])
        self.assertEqual("tau.agent_handoff.v1", decision["source"]["selected_schema"])
        self.assertEqual(14001, decision["source"]["selected_comment_id"])
        self.assertEqual("goal-guardian", decision["next"]["subagent"])
        self.assertEqual("either", decision["next"]["executor"])
        self.assertEqual(["next:goal-guardian", "executor:either"], decision["next"]["labels"])
        self.assertFalse(decision["would_mutate"])
        self.assertFalse(decision["orchestrator"]["would_mutate"])


if __name__ == "__main__":
    unittest.main()
