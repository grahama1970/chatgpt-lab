#!/usr/bin/env python3
"""Tests for dry-run route parsing over GitHub thread fixtures."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_ticket_route import load_json, route_fixture


class AgentTicketRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.goal = load_json(ROOT / "goals/current.json")
        self.trusted = {"grahama1970"}

    def decision(self, fixture_name: str) -> dict:
        fixture = load_json(ROOT / "examples/agent-harness/fixtures" / fixture_name)
        return route_fixture(fixture, self.goal, self.trusted)

    def test_human_interjection_preserve_goal_routes(self) -> None:
        decision = self.decision("issue-human-interjection-preserve-goal.json")
        self.assertEqual("ROUTE", decision["status"])
        self.assertEqual("chatgpt_lab.human_interjection.v1", decision["source"]["selected_schema"])
        self.assertEqual("reviewer", decision["next"]["subagent"])
        self.assertFalse(decision["would_mutate"])

    def test_human_goal_change_routes_to_goal_guardian(self) -> None:
        decision = self.decision("issue-human-interjection-goal-change.json")
        self.assertEqual("ROUTE", decision["status"])
        self.assertEqual("goal-guardian", decision["next"]["subagent"])

    def test_missing_next_subagent_refuses(self) -> None:
        decision = self.decision("issue-missing-next-subagent.json")
        self.assertEqual("REFUSED", decision["status"])
        self.assertEqual("invalid_actionable_block", decision["reason"])
        self.assertIn("next.subagent", decision["missing"])

    def test_generated_ticket_goal_mismatch_refuses(self) -> None:
        decision = self.decision("issue-generated-ticket-goal-mismatch.json")
        self.assertEqual("REFUSED", decision["status"])
        self.assertEqual("invalid_actionable_block", decision["reason"])
        self.assertTrue(any("goal_hash" in error for error in decision["errors"]))

    def test_legacy_phatgpt_task_is_detected_but_not_routed(self) -> None:
        decision = self.decision("issue-legacy-phatgpt-task-detected.json")
        self.assertEqual("REFUSED", decision["status"])
        self.assertEqual("legacy_phatgpt_task_detected_but_not_routable_in_this_slice", decision["reason"])

    def test_untrusted_human_interjection_refuses(self) -> None:
        fixture = load_json(ROOT / "examples/agent-harness/fixtures/issue-human-interjection-preserve-goal.json")
        fixture["comments"][0]["author"] = "not-graham"
        decision = route_fixture(fixture, self.goal, self.trusted)
        self.assertEqual("REFUSED", decision["status"])
        self.assertTrue(any("not trusted" in error for error in decision["errors"]))


if __name__ == "__main__":
    unittest.main()
