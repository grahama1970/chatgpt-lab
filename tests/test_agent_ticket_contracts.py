#!/usr/bin/env python3
"""Tests for goal-locked ticket contract validators."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal_contracts import (
    load_json,
    validate_agent_handoff,
    validate_generated_ticket,
    validate_human_interjection,
)


class AgentTicketContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.goal = load_json(ROOT / "goals/current.json")
        self.handoff = load_json(ROOT / "examples/agent-harness/agent-handoff.valid.json")
        self.human_interjection = load_json(
            ROOT / "examples/agent-harness/human-interjection.pause.valid.json"
        )
        self.generated_ticket = load_json(ROOT / "examples/agent-harness/generated-ticket.valid.json")

    def test_valid_examples_validate(self) -> None:
        self.assertEqual([], validate_agent_handoff(self.handoff, self.goal))
        self.assertEqual([], validate_human_interjection(self.human_interjection, self.goal))
        self.assertEqual([], validate_generated_ticket(self.generated_ticket, self.goal))

    def test_handoff_missing_next_subagent_blocks(self) -> None:
        mutated = copy.deepcopy(self.handoff)
        del mutated["next"]["subagent"]
        errors = validate_agent_handoff(mutated, self.goal)
        self.assertIn("handoff.next missing required field: subagent", errors)

    def test_pause_still_requires_explicit_next_human(self) -> None:
        mutated = copy.deepcopy(self.human_interjection)
        del mutated["next"]
        errors = validate_human_interjection(mutated, self.goal)
        self.assertIn("human_interjection missing required field: next", errors)

    def test_generated_ticket_goal_hash_mismatch_blocks(self) -> None:
        mutated = copy.deepcopy(self.generated_ticket)
        mutated["goal"]["goal_hash"] = "sha256:" + ("0" * 64)
        errors = validate_generated_ticket(mutated, self.goal)
        self.assertIn("generated_ticket.goal.goal_hash must match active goal hash", errors)

    def test_generated_ticket_with_amendment_routes_to_goal_guardian_or_human(self) -> None:
        mutated = copy.deepcopy(self.generated_ticket)
        mutated["goal_amendment_proposal"] = {"summary": "Change the goal."}
        mutated["handoff"]["next_subagent"] = "coder"
        mutated["handoff"]["next"]["subagent"] = "coder"
        mutated["ticket"]["labels"] = ["agent-work", "next:coder"]
        mutated["github"]["create"]["labels"] = ["agent-work", "next:coder"]
        mutated["github"]["labels"]["add"] = ["next:coder", "executor:either"]
        errors = validate_generated_ticket(mutated, self.goal)
        self.assertIn(
            "generated_ticket with goal_amendment_proposal must route to human or goal-guardian",
            errors,
        )

    def test_github_projection_must_match_next_route(self) -> None:
        mutated = copy.deepcopy(self.handoff)
        mutated["github"]["labels"]["add"] = ["next:coder", "executor:either"]
        errors = validate_agent_handoff(mutated, self.goal)
        self.assertIn("handoff.github.labels.add must include next:reviewer", errors)


if __name__ == "__main__":
    unittest.main()
