#!/usr/bin/env python3
"""Tests for compact Tau agent-facing contracts."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal_contracts import load_json
from tau_contracts import validate_tau_contract


class TauContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.goal = load_json(ROOT / "goals/current.json")
        self.handoff = load_json(ROOT / "examples/agent-harness/tau/tau-agent-handoff.valid.json")
        self.generated_ticket = load_json(ROOT / "examples/agent-harness/tau/tau-generated-ticket.valid.json")
        self.goal_change = load_json(ROOT / "examples/agent-harness/tau/tau-human-goal-change.valid.json")

    def test_tau_handoff_defaults_executor_and_routes(self) -> None:
        errors, decision = validate_tau_contract(self.handoff, self.goal)
        self.assertEqual([], errors)
        self.assertIsNotNone(decision)
        assert decision is not None
        self.assertEqual("ROUTE", decision["status"])
        self.assertEqual("reviewer", decision["next"]["subagent"])
        self.assertEqual("either", decision["next"]["executor"])
        self.assertEqual(["next:reviewer", "executor:either"], decision["next"]["labels"])
        self.assertFalse(decision["would_mutate"])

    def test_tau_generated_ticket_routes_without_projecting_labels(self) -> None:
        errors, decision = validate_tau_contract(self.generated_ticket, self.goal)
        self.assertEqual([], errors)
        self.assertIsNotNone(decision)
        assert decision is not None
        self.assertEqual("tau.generated_ticket.v1", decision["source"]["selected_schema"])
        self.assertEqual("issue", decision["source"]["kind"])
        self.assertEqual("reviewer", decision["next"]["subagent"])

    def test_tau_human_goal_change_requires_goal_guardian(self) -> None:
        errors, decision = validate_tau_contract(self.goal_change, self.goal, trusted_human="grahama1970")
        self.assertEqual([], errors)
        self.assertIsNotNone(decision)
        assert decision is not None
        self.assertEqual("goal-guardian", decision["next"]["subagent"])

    def test_goal_hash_mismatch_refuses(self) -> None:
        mutated = copy.deepcopy(self.handoff)
        mutated["goal"]["goal_hash"] = "sha256:" + ("0" * 64)
        errors, decision = validate_tau_contract(mutated, self.goal)
        self.assertIn("tau_handoff.goal.goal_hash must match active goal hash", errors)
        self.assertIsNone(decision)

    def test_unknown_next_agent_refuses(self) -> None:
        mutated = copy.deepcopy(self.handoff)
        mutated["next_agent"]["name"] = "unbounded-agent"
        errors, decision = validate_tau_contract(mutated, self.goal)
        self.assertIn("tau_handoff.next_agent.name must be a recognized agent", errors)
        self.assertIsNone(decision)

    def test_generated_ticket_amendment_must_route_to_human_or_goal_guardian(self) -> None:
        mutated = copy.deepcopy(self.generated_ticket)
        mutated["goal_amendment_proposal"] = {"summary": "Change the goal"}
        mutated["next_agent"]["name"] = "coder"
        errors, decision = validate_tau_contract(mutated, self.goal)
        self.assertIn(
            "tau_generated_ticket with goal_amendment_proposal must route to human or goal-guardian",
            errors,
        )
        self.assertIsNone(decision)

    def test_human_goal_change_rejects_untrusted_human(self) -> None:
        errors, decision = validate_tau_contract(self.goal_change, self.goal, trusted_human="not-graham")
        self.assertIn("tau_human_goal_change author must be trusted human", errors)
        self.assertIsNone(decision)

    def test_human_goal_change_rejects_non_human_actor(self) -> None:
        mutated = copy.deepcopy(self.goal_change)
        mutated["previous_subagent"] = "coder"
        errors, decision = validate_tau_contract(mutated, self.goal, trusted_human="grahama1970")
        self.assertIn("tau_human_goal_change.previous_subagent must be human", errors)
        self.assertIsNone(decision)


if __name__ == "__main__":
    unittest.main()
