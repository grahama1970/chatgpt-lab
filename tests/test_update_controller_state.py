import unittest

from scripts import update_controller_state


class UpdateControllerStateTest(unittest.TestCase):
    def test_latest_release_evidence_gates_are_ready_for_next_task(self):
        state = update_controller_state.build_state("2026-06-27T20:30:00Z")

        self.assertEqual(state["current_iteration"]["iteration_id"], "2026-06-27-phatgpt-e2e-sanity")
        self.assertEqual(state["phase"], "awaiting-next-webgpt-task")
        self.assertEqual(state["state"], "READY_FOR_NEXT_TASK")
        self.assertEqual(state["latest_release"]["pr"], 19)
        self.assertEqual(
            state["latest_release"]["merge_commit"],
            "c9472f78d5c0e00f7323360328169a343a827fb2",
        )
        self.assertEqual(
            state["latest_release"]["proof_commit"],
            "c9472f78d5c0e00f7323360328169a343a827fb2",
        )
        self.assertTrue(all(gate["status"] == "PASS" for gate in state["gates"]))


if __name__ == "__main__":
    unittest.main()
