"""Quantum Teleportation Lab — Simplified Streamlit App (NumPy + Plotly)."""

import numpy as np
import streamlit as st

from quantum.teleportation import (
    TeleportationResult,
    create_input_state,
    run_multiple_trials,
    run_teleportation_experiment,
)
from visualization import (
    create_bloch_sphere_figure,
    create_circuit_diagram_figure,
    create_fidelity_history_chart,
    create_measurement_probabilities_chart,
)

st.set_page_config(page_title="Quantum Teleportation Lab", page_icon="⚛️", layout="wide")

CUSTOM_CSS = """
<style>
.stApp { background: #0b1120; color: #e2e8f0; }
.dirac-box {
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 8px; padding: 10px;
    font-family: monospace; font-size: 1.05rem; font-weight: 600;
    color: #38bdf8; text-align: center; margin: 8px 0;
}
.metric-badge {
    background: rgba(30, 41, 59, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 8px; padding: 12px; text-align: center;
}
.metric-value { font-size: 1.4rem; font-weight: 700; color: #38bdf8; font-family: monospace; }
.metric-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; margin-top: 4px; }
.step-pill {
    display: inline-block; padding: 4px 10px; border-radius: 6px;
    font-size: 0.8rem; font-weight: 600; margin: 0 6px 6px 0;
}
.step-done { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; }
.step-active { background: rgba(56, 189, 248, 0.25); border: 1px solid #38bdf8; color: #38bdf8; }
.step-pending { background: rgba(51, 65, 85, 0.4); border: 1px solid #475569; color: #64748b; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session defaults
defaults = {
    "theta_deg": 45.0,
    "phi_deg": 30.0,
    "current_step": 6,
    "step_mode": False,
    "experiment_result": None,
    "trials_data": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def format_complex(z: complex) -> str:
    return f"{float(np.real(z)):.4f} + {float(np.imag(z)):.4f}i"


# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
def update_walkthrough_mode():
    if st.session_state.step_mode:
        st.session_state.current_step = 1
    else:
        st.session_state.current_step = 6


with st.sidebar:
    st.markdown("### Experimental Controls")
    st.markdown("---")
    st.markdown("#### Input Quantum State |ψ⟩")

    presets = [
        ("|0⟩", 0.0, 0.0), ("|1⟩", 180.0, 0.0), ("|+⟩", 90.0, 0.0),
        ("|−⟩", 90.0, 180.0), ("|+i⟩", 90.0, 90.0), ("|−i⟩", 90.0, 270.0),
    ]
    cols = st.columns(3)
    for idx, (label, t_deg, p_deg) in enumerate(presets):
        with cols[idx % 3]:
            if st.button(label, use_container_width=True):
                st.session_state.theta_deg = t_deg
                st.session_state.phi_deg = p_deg

    st.session_state.theta_deg = st.slider(
        "Polar angle θ (°)", 0.0, 180.0, float(st.session_state.theta_deg), 1.0
    )
    st.session_state.phi_deg = st.slider(
        "Azimuthal angle φ (°)", 0.0, 360.0, float(st.session_state.phi_deg), 1.0
    )

    current_input_state = create_input_state(st.session_state.theta_deg, st.session_state.phi_deg)
    st.markdown(f"<div class='dirac-box'>{current_input_state.dirac_notation()}</div>", unsafe_allow_html=True)
    st.latex(r"\alpha = \cos(\theta/2), \quad \beta = e^{i\phi}\sin(\theta/2)")

    st.markdown("---")
    st.markdown("#### Execution Mode")
    st.toggle(
        "Step-by-step Walkthrough",
        key="step_mode",
        on_change=update_walkthrough_mode,
    )
    if st.session_state.step_mode:
        c_prev, c_next = st.columns(2)
        with c_prev:
            if st.button("Previous Step", use_container_width=True, disabled=(st.session_state.current_step <= 1)):
                st.session_state.current_step = max(1, st.session_state.current_step - 1)
        with c_next:
            if st.button("Next Step", use_container_width=True, disabled=(st.session_state.current_step >= 6)):
                st.session_state.current_step = min(6, st.session_state.current_step + 1)

    st.markdown("---")
    run_clicked = st.button("Execute Teleportation Protocol", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("#### Repeated Experimental Trials")
    num_trials = st.number_input("Number of Trials", min_value=10, max_value=2000, value=200, step=50)
    if st.button("Run Batch Trials", use_container_width=True):
        st.session_state.trials_data = run_multiple_trials(current_input_state, int(num_trials))

# Re-run experiment when button is clicked, on first load, or when input angles change
prev_res: TeleportationResult = st.session_state.experiment_result
state_changed = (
    prev_res is None
    or prev_res.input_state.theta != current_input_state.theta
    or prev_res.input_state.phi != current_input_state.phi
)
if run_clicked or state_changed:
    st.session_state.experiment_result = run_teleportation_experiment(current_input_state)

res: TeleportationResult = st.session_state.experiment_result

# ---------------------------------------------------------
# Header & Top Metrics
# ---------------------------------------------------------
st.title("⚛️ Quantum Teleportation Lab")
st.caption("3-Qubit Quantum Teleportation Protocol (BBCJPW 1993) simulated with NumPy state vectors.")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-badge'><div class='metric-value'>|{res.m0}{res.m1}⟩</div><div class='metric-label'>Bell Measurement (m₀, m₁)</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-badge'><div class='metric-value'>{res.measurement_outcome_prob * 100:.1f}%</div><div class='metric-label'>Outcome Probability</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-badge'><div class='metric-value' style='color:#10b981;'>{res.fidelity:.4f}</div><div class='metric-label'>State Fidelity F</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-badge'><div class='metric-value' style='font-size:1.05rem; color:#c084fc;'>{res.correction_description}</div><div class='metric-label'>Bob's Correction Applied</div></div>", unsafe_allow_html=True)

if st.session_state.trials_data is not None:
    trials = st.session_state.trials_data
    st.success(
        f"Batch complete: {trials['num_trials']} trials, average fidelity "
        f"{trials['avg_fidelity']:.4f}. See the Repeated Trials & Statistics tab for details."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6-Stage Protocol Walkthrough
# ---------------------------------------------------------
st.subheader("Protocol Execution Walkthrough")
pills_html = ""
for s_idx in range(1, 7):
    if s_idx < st.session_state.current_step:
        cls, label = "step-done", "Completed"
    elif s_idx == st.session_state.current_step:
        cls, label = "step-active", "Active"
    else:
        cls, label = "step-pending", "Pending"
    pills_html += f"<span class='step-pill {cls}'>Stage {s_idx}: {label}</span>"
st.markdown(pills_html, unsafe_allow_html=True)

stage_info = res.stages[st.session_state.current_step - 1]
st.markdown(f"**Stage {st.session_state.current_step}: {stage_info.name}**")
st.info(stage_info.description)

# ---------------------------------------------------------
# Visualizations & Theory Tabs
# ---------------------------------------------------------
tab_visuals, tab_trials, tab_theory = st.tabs([
    "Quantum Circuit & Bloch Sphere",
    "Repeated Trials & Statistics",
    "Protocol Mathematics",
])

with tab_visuals:
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Quantum Circuit Schematic")
        st.plotly_chart(
            create_circuit_diagram_figure(res, highlight_stage=st.session_state.current_step),
            use_container_width=True, config={"displayModeBar": False},
        )
        st.markdown("#### Bell Measurement Probabilities")
        counts = st.session_state.trials_data["outcome_counts"] if st.session_state.trials_data else None
        total = st.session_state.trials_data["num_trials"] if st.session_state.trials_data else 0
        st.plotly_chart(
            create_measurement_probabilities_chart(res.all_outcome_probs, counts, total),
            use_container_width=True, config={"displayModeBar": False},
        )

    with col_right:
        st.markdown("#### 3D Bloch Sphere Comparison")
        st.plotly_chart(
            create_bloch_sphere_figure(current_input_state, res.bob_state_obj),
            use_container_width=True, config={"displayModeBar": False},
        )
        st.markdown("#### State Amplitudes Comparison")
        st.table({
            "Basis": ["|0⟩", "|1⟩"],
            "Alice Original": [
                format_complex(current_input_state.alpha),
                format_complex(current_input_state.beta),
            ],
            "Bob Reconstructed": [
                format_complex(res.bob_state_obj.alpha),
                format_complex(res.bob_state_obj.beta),
            ],
        })

with tab_trials:
    st.markdown("#### Repeated Experimental Teleportation Runs")
    if st.session_state.trials_data is None:
        st.info("Click 'Run Batch Trials' in the sidebar to see statistics across multiple runs.")
    else:
        td = st.session_state.trials_data
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Trials", f"{td['num_trials']}")
        c2.metric("Average Fidelity", f"{td['avg_fidelity']:.4f}")
        c3.metric("Success Rate (F > 0.999)", f"{td['success_rate'] * 100:.1f}%")
        c4.metric("Fidelity Range", f"[{td['min_fidelity']:.4f}, {td['max_fidelity']:.4f}]")

        t_left, t_right = st.columns(2)
        with t_left:
            st.plotly_chart(create_fidelity_history_chart(td["fidelities"]),
                            use_container_width=True, config={"displayModeBar": False})
        with t_right:
            st.markdown("#### Outcome Frequency Distribution")
            outcomes = ["00", "01", "10", "11"]
            st.dataframe({
                "Outcome": [f"|{k}⟩" for k in outcomes],
                "Count": [td["outcome_counts"][k] for k in outcomes],
                "Observed %": [f"{(td['outcome_counts'][k] / td['num_trials']) * 100:.2f}%" for k in outcomes],
                "Theoretical %": ["25.00%"] * 4,
            }, use_container_width=True, hide_index=True)

with tab_theory:
    st.markdown(r"""
    Alice wants to send an unknown qubit state $|\psi\rangle_0 = \alpha|0\rangle + \beta|1\rangle$ to Bob using a shared Bell pair:
    $$|\Phi^+\rangle_{12} = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$

    1. **Initial 3-Qubit State:** $|\Psi_0\rangle = |\psi\rangle_0 \otimes |\Phi^+\rangle_{12}$
    2. **Alice's Gates:** $\text{CNOT}(q_0 \to q_1)$ followed by $H(q_0)$ yields:
       $$|\Psi_2\rangle = \frac{1}{2}\Big(|00\rangle(\alpha|0\rangle+\beta|1\rangle) + |01\rangle(\alpha|1\rangle+\beta|0\rangle) + |10\rangle(\alpha|0\rangle-\beta|1\rangle) + |11\rangle(\alpha|1\rangle-\beta|0\rangle)\Big)$$
    3. **Measurement & Bob's Correction ($U = Z^{m_0} X^{m_1}$):**

    | Outcome $(m_0, m_1)$ | Bob's State Before Correction | Correction Applied | Final State |
    | :---: | :---: | :---: | :---: |
    | **00** | $\alpha\|0\rangle + \beta\|1\rangle$ | $I$ (None) | $\|\psi\rangle$ |
    | **01** | $\alpha\|1\rangle + \beta\|0\rangle$ | $X$ | $\|\psi\rangle$ |
    | **10** | $\alpha\|0\rangle - \beta\|1\rangle$ | $Z$ | $\|\psi\rangle$ |
    | **11** | $\alpha\|1\rangle - \beta\|0\rangle$ | $Z X$ | $\|\psi\rangle$ |
    """)
