"""Unit tests for the NumPy quantum teleportation protocol."""

import unittest
import numpy as np
from quantum.teleportation import (
    create_input_state,
    run_multiple_trials,
    run_teleportation_experiment,
)


class TestQuantumTeleportation(unittest.TestCase):
    def test_input_state_is_normalized(self):
        for theta in [0, 45, 90, 135, 180]:
            for phi in [0, 60, 180, 270]:
                state = create_input_state(theta, phi)
                self.assertTrue(np.isclose(np.linalg.norm(state.vector), 1.0, atol=1e-10))

    def test_all_four_outcomes_reconstruct_state_with_unit_fidelity(self):
        test_states = [
            (0, 0),      # |0>
            (180, 0),    # |1>
            (90, 0),     # |+>
            (90, 180),   # |->
            (90, 90),    # |+i>
            (37.5, 112.3),
            (124.8, 235.1),
        ]
        for theta, phi in test_states:
            input_state = create_input_state(theta, phi)
            for m0 in (0, 1):
                for m1 in (0, 1):
                    res = run_teleportation_experiment(input_state, forced_measurement=(m0, m1))
                    self.assertEqual((res.m0, res.m1), (m0, m1))
                    self.assertAlmostEqual(res.fidelity, 1.0, places=6)
                    self.assertTrue(
                        np.allclose(input_state.bloch_coords, res.bob_state_obj.bloch_coords, atol=1e-5)
                    )

    def test_outcome_probabilities_are_uniform(self):
        state = create_input_state(60.0, 45.0)
        res = run_teleportation_experiment(state, seed=7)
        self.assertAlmostEqual(sum(res.all_outcome_probs.values()), 1.0, places=7)
        for prob in res.all_outcome_probs.values():
            self.assertAlmostEqual(prob, 0.25, places=6)

    def test_batch_trials_statistics(self):
        state = create_input_state(60.0, 30.0)
        stats = run_multiple_trials(state, num_trials=200, seed=42)
        self.assertEqual(stats["num_trials"], 200)
        self.assertEqual(stats["successful_trials"], 200)
        self.assertAlmostEqual(stats["avg_fidelity"], 1.0, places=6)
        for count in stats["outcome_counts"].values():
            freq = count / 200.0
            self.assertTrue(0.15 <= freq <= 0.35)


if __name__ == "__main__":
    unittest.main()
