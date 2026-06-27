#!/usr/bin/env python3
"""Tests for the goal capsule validator."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal_contracts import compute_goal_hash, load_json, validate_goal_capsule


class GoalCapsuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.goal = load_json(ROOT / "goals/current.json")

    def test_current_goal_capsule_validates(self) -> None:
        self.assertEqual([], validate_goal_capsule(self.goal))

    def test_goal_hash_is_deterministic(self) -> None:
        self.assertEqual(self.goal["goal_hash"], compute_goal_hash(self.goal))

    def test_non_human_owner_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.goal)
        mutated["owner"] = "webgpt"
        errors = validate_goal_capsule(mutated)
        self.assertIn("goal.owner must be human", errors)

    def test_stale_goal_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.goal)
        mutated["success_criteria"].append("A changed criterion without a new hash.")
        errors = validate_goal_capsule(mutated)
        self.assertTrue(any(error.startswith("goal.goal_hash must equal") for error in errors))


if __name__ == "__main__":
    unittest.main()
