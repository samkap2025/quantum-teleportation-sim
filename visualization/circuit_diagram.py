"""Interactive Quantum Circuit Diagram visualization using Plotly."""

from typing import Optional
import plotly.graph_objects as go
from quantum.teleportation import TeleportationResult


def create_circuit_diagram_figure(
    result: Optional[TeleportationResult] = None,
    highlight_stage: Optional[int] = None,
) -> go.Figure:
    """Draws the 3-qubit quantum teleportation circuit with active-stage highlighting."""
    fig = go.Figure()
    x_max = 10.0

    # Quantum wires (q0, q1, q2) and classical wires (c0, c1)
    for y_pos, name in [(4.0, "q₀ |ψ⟩"), (3.0, "q₁ |0⟩"), (2.0, "q₂ |0⟩")]:
        fig.add_trace(go.Scatter(
            x=[0.5, x_max], y=[y_pos, y_pos], mode="lines",
            line=dict(color="#475569", width=2.5), hoverinfo="none", showlegend=False,
        ))
        fig.add_annotation(x=0.4, y=y_pos, text=name, showarrow=False,
                           font=dict(color="#94a3b8", size=13, family="monospace"), xanchor="right")

    for y_pos, name in [(0.8, "c₀ (m₀)"), (0.4, "c₁ (m₁)")]:
        fig.add_trace(go.Scatter(
            x=[0.5, x_max], y=[y_pos, y_pos], mode="lines",
            line=dict(color="#64748b", width=1.5), hoverinfo="none", showlegend=False,
        ))
        fig.add_annotation(x=0.4, y=y_pos, text=name, showarrow=False,
                           font=dict(color="#64748b", size=11, family="monospace"), xanchor="right")

    # Stage 1: Alice prepares the input state on q0
    _draw_gate_box(
        fig,
        x=1.0,
        y=4.0,
        label="RY/P",
        color="#06b6d4",
        active=(highlight_stage == 1),
    )

    # Stage 2: Bell pair creation (H on q1, CNOT 1->2)
    _draw_gate_box(fig, x=1.5, y=3.0, label="H", color="#a855f7", active=(highlight_stage == 2))
    _draw_cnot(fig, x_ctrl=2.5, y_ctrl=3.0, y_tgt=2.0, color="#a855f7", active=(highlight_stage == 2))

    # Stage 3: Alice's Bell analysis (CNOT 0->1, H on q0)
    _draw_cnot(fig, x_ctrl=3.8, y_ctrl=4.0, y_tgt=3.0, color="#06b6d4", active=(highlight_stage == 3))
    _draw_gate_box(fig, x=4.8, y=4.0, label="H", color="#06b6d4", active=(highlight_stage == 3))

    # Stage 4: Measurements on q0 and q1
    _draw_measurement(fig, x=5.8, y=4.0, target_c_y=0.8, label="M₀", active=(highlight_stage == 4))
    _draw_measurement(fig, x=5.8, y=3.0, target_c_y=0.4, label="M₁", active=(highlight_stage == 4))

    # Stage 5 & 6: Conditional X (from m1) and Z (from m0) on Bob's q2
    x_active = bool(result and result.m1 == 1)
    z_active = bool(result and result.m0 == 1)
    corr_stage = highlight_stage == 6
    _draw_cond_correction(fig, x=7.5, y_qubit=2.0, y_class=0.4, label="X", is_active=x_active, stage_active=corr_stage)
    _draw_cond_correction(fig, x=8.7, y_qubit=2.0, y_class=0.8, label="Z", is_active=z_active, stage_active=corr_stage)

    fig.add_annotation(
        x=9.8, y=2.0, text="|ψ_Bob⟩", showarrow=False,
        font=dict(color="#10b981", size=13, family="monospace"),
        bgcolor="rgba(16, 185, 129, 0.2)", bordercolor="#10b981", borderwidth=1, borderpad=4,
    )

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 10.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.1, 4.6]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
    )
    return fig


def _draw_gate_box(fig: go.Figure, x: float, y: float, label: str, color: str, active: bool = False):
    border = "#ffffff" if active else color
    fig.add_shape(
        type="rect", x0=x - 0.3, y0=y - 0.35, x1=x + 0.3, y1=y + 0.35,
        line=dict(color=border, width=2.5 if active else 1.5),
        fillcolor=color if active else "rgba(30, 41, 59, 0.9)",
    )
    fig.add_annotation(
        x=x, y=y, text=label, showarrow=False,
        font=dict(color="#ffffff" if active else color, size=13, family="monospace"),
    )


def _draw_cnot(fig: go.Figure, x_ctrl: float, y_ctrl: float, y_tgt: float, color: str, active: bool = False):
    line_w = 3 if active else 2
    fig.add_trace(go.Scatter(
        x=[x_ctrl, x_ctrl], y=[y_ctrl, y_tgt], mode="lines",
        line=dict(color=color, width=line_w), hoverinfo="none", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[x_ctrl], y=[y_ctrl], mode="markers",
        marker=dict(size=12, color=color), hoverinfo="none", showlegend=False,
    ))
    fig.add_shape(
        type="circle", x0=x_ctrl - 0.25, y0=y_tgt - 0.25, x1=x_ctrl + 0.25, y1=y_tgt + 0.25,
        line=dict(color=color, width=line_w), fillcolor="rgba(15, 23, 42, 0.8)",
    )
    fig.add_trace(go.Scatter(
        x=[x_ctrl, x_ctrl], y=[y_tgt - 0.25, y_tgt + 0.25], mode="lines",
        line=dict(color=color, width=line_w), hoverinfo="none", showlegend=False,
    ))


def _draw_measurement(fig: go.Figure, x: float, y: float, target_c_y: float, label: str, active: bool = False):
    border = "#38bdf8" if active else "#94a3b8"
    fig.add_shape(
        type="rect", x0=x - 0.32, y0=y - 0.35, x1=x + 0.32, y1=y + 0.35,
        line=dict(color=border, width=2), fillcolor="rgba(30, 41, 59, 0.95)",
    )
    fig.add_annotation(x=x, y=y, text=label, showarrow=False,
                       font=dict(color=border, size=11, family="monospace"))
    fig.add_trace(go.Scatter(
        x=[x, x], y=[y - 0.35, target_c_y], mode="lines",
        line=dict(color=border, width=1.5, dash="dot"), hoverinfo="none", showlegend=False,
    ))


def _draw_cond_correction(fig: go.Figure, x: float, y_qubit: float, y_class: float, label: str, is_active: bool, stage_active: bool):
    color = "#10b981" if is_active else ("#94a3b8" if stage_active else "#64748b")
    fig.add_trace(go.Scatter(
        x=[x, x], y=[y_class, y_qubit - 0.35], mode="lines",
        line=dict(color=color, width=2, dash="dash"), hoverinfo="none", showlegend=False,
    ))
    fig.add_shape(
        type="rect", x0=x - 0.3, y0=y_qubit - 0.35, x1=x + 0.3, y1=y_qubit + 0.35,
        line=dict(color=color, width=2),
        fillcolor="rgba(16, 185, 129, 0.25)" if is_active else "rgba(30, 41, 59, 0.9)",
    )
    fig.add_annotation(x=x, y=y_qubit, text=label, showarrow=False,
                       font=dict(color=color, size=13, family="monospace"))
