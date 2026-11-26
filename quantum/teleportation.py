"""Three-qubit quantum teleportation state-vector simulation using NumPy."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


_HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
_PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
_PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)


@dataclass
class QuantumState:
    """Single-qubit pure state |psi> = alpha|0> + beta|1>."""
    alpha: complex
    beta: complex
    theta: float  # polar angle in radians [0, pi]
    phi: float    # azimuthal angle in radians [0, 2*pi)

    @property
    def vector(self) -> np.ndarray:
        return np.array([self.alpha, self.beta], dtype=complex)

    @property
    def bloch_coords(self) -> Tuple[float, float, float]:
        """Bloch sphere coordinates (x, y, z)."""
        return (
            float(np.sin(self.theta) * np.cos(self.phi)),
            float(np.sin(self.theta) * np.sin(self.phi)),
            float(np.cos(self.theta)),
        )

    def dirac_notation(self, precision: int = 3) -> str:
        """Human-readable Dirac notation string."""
        def fmt(z: complex) -> str:
            r, i = float(np.real(z)), float(np.imag(z))
            if abs(i) < 1e-6:
                return f"{r:.{precision}f}"
            if abs(r) < 1e-6:
                return f"{i:+.{precision}f}i"
            sign = "+" if i >= 0 else "-"
            return f"({r:.{precision}f} {sign} {abs(i):.{precision}f}i)"

        return f"|ψ⟩ = {fmt(self.alpha)}|0⟩ + {fmt(self.beta)}|1⟩"


@dataclass
class CircuitStage:
    """Description of one protocol stage for the UI walkthrough."""
    stage_id: int
    name: str
    description: str
    state_vector: np.ndarray


@dataclass
class TeleportationResult:
    """Complete result of a single quantum teleportation run."""
    input_state: QuantumState
    m0: int
    m1: int
    measurement_outcome_prob: float
    all_outcome_probs: Dict[str, float]
    bob_state_obj: QuantumState
    fidelity: float
    correction_description: str
    stages: List[CircuitStage] = field(default_factory=list)


def create_input_state(theta_deg: float, phi_deg: float) -> QuantumState:
    """Creates |psi> = cos(theta/2)|0> + exp(i*phi)sin(theta/2)|1>."""
    theta = float(np.radians(theta_deg))
    phi = float(np.radians(phi_deg))

    return QuantumState(
        alpha=complex(np.cos(theta / 2.0)),
        beta=complex(np.exp(1.0j * phi) * np.sin(theta / 2.0)),
        theta=theta,
        phi=phi,
    )


def state_from_vector(vec: np.ndarray) -> QuantumState:
    """Converts a 2-element complex state vector into a QuantumState (up to global phase)."""
    v = np.asarray(vec, dtype=complex).flatten()
    v = v / np.linalg.norm(v)

    # Remove global phase so alpha is real and non-negative
    phase = np.angle(v[0]) if abs(v[0]) > 1e-9 else np.angle(v[1])
    v_clean = v * np.exp(-1.0j * phase)

    alpha, beta = v_clean[0], v_clean[1]
    theta = 2.0 * float(np.arccos(np.clip(np.abs(alpha), 0.0, 1.0)))
    phi = float(np.angle(beta)) % (2.0 * np.pi) if abs(np.sin(theta / 2.0)) > 1e-7 else 0.0

    return QuantumState(alpha=complex(alpha), beta=complex(beta), theta=theta, phi=phi)


def _apply_single_qubit_gate(state: np.ndarray, gate: np.ndarray, qubit: int) -> np.ndarray:
    """Applies a 2x2 gate to one qubit in a little-endian state vector."""
    updated = np.empty_like(state)
    qubit_mask = 1 << qubit
    for index in range(state.size):
        if index & qubit_mask:
            continue
        paired_index = index | qubit_mask
        updated[index] = gate[0, 0] * state[index] + gate[0, 1] * state[paired_index]
        updated[paired_index] = gate[1, 0] * state[index] + gate[1, 1] * state[paired_index]
    return updated


def _apply_controlled_x(state: np.ndarray, control: int, target: int) -> np.ndarray:
    """Applies a CNOT gate to a little-endian state vector."""
    updated = np.empty_like(state)
    control_mask = 1 << control
    target_mask = 1 << target
    for index in range(state.size):
        source_index = index ^ target_mask if index & control_mask else index
        updated[index] = state[source_index]
    return updated


def run_teleportation_experiment(
    input_state: QuantumState,
    forced_measurement: Optional[Tuple[int, int]] = None,
    seed: Optional[int] = None,
) -> TeleportationResult:
    """Executes the 3-qubit quantum teleportation protocol with NumPy state vectors."""
    # Stage 1: Prepare Alice's input state on q0 (q1=|0>, q2=|0>)
    s1 = np.zeros(8, dtype=complex)
    s1[0] = np.cos(input_state.theta / 2.0)
    s1[1] = np.exp(1.0j * input_state.phi) * np.sin(input_state.theta / 2.0)

    # Stage 2: Create entangled Bell pair |Phi+> between q1 (Alice) and q2 (Bob)
    s2 = _apply_single_qubit_gate(s1, _HADAMARD, 1)
    s2 = _apply_controlled_x(s2, control=1, target=2)

    # Stage 3: Alice entangles q0 with q1 and applies Hadamard to q0
    s3 = _apply_controlled_x(s2, control=0, target=1)
    s3 = _apply_single_qubit_gate(s3, _HADAMARD, 0)

    # Qubit 0 is the least-significant state-vector bit.
    all_probs = {
        f"{m0}{m1}": float(sum(
            abs(s3[index]) ** 2
            for index in range(8)
            if (index & 1) == m0 and ((index >> 1) & 1) == m1
        ))
        for m0 in (0, 1)
        for m1 in (0, 1)
    }

    # Stage 4: Measure Alice's qubits q0 and q1
    if forced_measurement is not None:
        m0, m1 = forced_measurement
    else:
        outcomes = [(m0, m1) for m0 in (0, 1) for m1 in (0, 1)]
        probabilities = [all_probs[f"{m0}{m1}"] for m0, m1 in outcomes]
        rng = np.random.default_rng(seed)
        m0, m1 = outcomes[int(rng.choice(len(outcomes), p=probabilities))]

    collapsed = np.zeros_like(s3)
    for index in range(8):
        if (index & 1) == m0 and ((index >> 1) & 1) == m1:
            collapsed[index] = s3[index]
    norm = np.linalg.norm(collapsed)
    if norm < 1e-12:
        raise ValueError(f"Outcome ({m0}, {m1}) has zero probability.")
    collapsed /= norm

    prob = all_probs[f"{m0}{m1}"]

    # Stage 6: Apply Bob's conditional corrections (X if m1=1, Z if m0=1)
    applied_gates = []
    if m1 == 1:
        applied_gates.append("X (bit m₁=1)")
    if m0 == 1:
        applied_gates.append("Z (bit m₀=1)")

    correction_desc = " + ".join(applied_gates) if applied_gates else "Identity (no correction needed)"
    final_state = collapsed
    if m1 == 1:
        final_state = _apply_single_qubit_gate(final_state, _PAULI_X, 2)
    if m0 == 1:
        final_state = _apply_single_qubit_gate(final_state, _PAULI_Z, 2)

    # Extract Bob's single-qubit state (q2) and compute fidelity with Alice's input state
    bob_sv = np.array([
        final_state[(q2 << 2) | (m1 << 1) | m0]
        for q2 in (0, 1)
    ], dtype=complex)
    fidelity = float(np.clip(abs(np.vdot(input_state.vector, bob_sv)) ** 2, 0.0, 1.0))
    bob_state_obj = state_from_vector(bob_sv)

    stages = [
        CircuitStage(1, "Input State Preparation", "Alice prepares |ψ⟩ on Qubit 0. Qubits 1 and 2 start in |0⟩.", s1),
        CircuitStage(2, "Entanglement Generation", "H(q1) and CNOT(q1 → q2) create Bell pair |Φ+⟩ between Alice and Bob.", s2),
        CircuitStage(3, "Alice's Bell Analysis", "Alice applies CNOT(q0 → q1) and H(q0).", s3),
        CircuitStage(4, "Bell-State Measurement", f"Alice measures q0 and q1: m₀={m0}, m₁={m1} (p={prob:.3f}).", collapsed),
        CircuitStage(5, "Classical Communication", f"Alice sends classical bits (m₀={m0}, m₁={m1}) to Bob.", collapsed),
        CircuitStage(6, "Bob's Correction & Reconstruction", f"Bob applies {correction_desc}. Fidelity F = {fidelity:.4f}.", bob_sv),
    ]

    return TeleportationResult(
        input_state=input_state,
        m0=m0,
        m1=m1,
        measurement_outcome_prob=prob,
        all_outcome_probs=all_probs,
        bob_state_obj=bob_state_obj,
        fidelity=fidelity,
        correction_description=correction_desc,
        stages=stages,
    )


def run_multiple_trials(
    input_state: QuantumState,
    num_trials: int,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Runs repeated teleportation trials to verify the ~25% Bell outcome distribution."""
    rng = np.random.default_rng(seed)
    outcome_counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    fidelities: List[float] = []

    for _ in range(num_trials):
        trial_seed = int(rng.integers(0, 2**31 - 1))
        res = run_teleportation_experiment(input_state=input_state, seed=trial_seed)
        outcome_counts[f"{res.m0}{res.m1}"] += 1
        fidelities.append(res.fidelity)

    fidelities_arr = np.array(fidelities, dtype=float)
    successful = int(np.sum(fidelities_arr > 0.999))

    return {
        "num_trials": num_trials,
        "outcome_counts": outcome_counts,
        "fidelities": fidelities,
        "avg_fidelity": float(np.mean(fidelities_arr)),
        "min_fidelity": float(np.min(fidelities_arr)),
        "max_fidelity": float(np.max(fidelities_arr)),
        "successful_trials": successful,
        "success_rate": float(successful / num_trials) if num_trials > 0 else 0.0,
    }
