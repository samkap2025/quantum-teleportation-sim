"""Regression tests for the Streamlit walkthrough controls."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class TestAppInteractions(unittest.TestCase):
    def test_state_change_and_execute_complete_without_app_error(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path)).run()

        app.slider[0].set_value(90).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertAlmostEqual(
            app.session_state["experiment_result"].input_state.theta,
            1.5707963267948966,
        )

        next(button for button in app.button if button.label == "Execute Teleportation Protocol").click().run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertAlmostEqual(app.session_state["experiment_result"].fidelity, 1.0)

    def test_next_step_advances_without_app_error(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path)).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])

        app.toggle[0].set_value(True).run()
        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertEqual(app.session_state["current_step"], 1)

        next_button = next(button for button in app.button if button.label == "Next Step")
        next_button.click().run()

        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertEqual(app.session_state["current_step"], 2)

    def test_batch_trials_show_completion_feedback(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path)).run()
        app.number_input[0].set_value(10).run()
        next(button for button in app.button if button.label == "Run Batch Trials").click().run()

        self.assertFalse(app.exception, [str(error.value) for error in app.exception])
        self.assertEqual(app.session_state["trials_data"]["num_trials"], 10)
        self.assertTrue(any("Batch complete: 10 trials" in alert.value for alert in app.success))


if __name__ == "__main__":
    unittest.main()
