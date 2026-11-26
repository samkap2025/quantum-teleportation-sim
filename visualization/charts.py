"""Measurement statistics and fidelity comparison charts using Plotly."""

from typing import Dict, List, Optional
import plotly.graph_objects as go


def create_measurement_probabilities_chart(
    all_probs: Dict[str, float],
    observed_counts: Optional[Dict[str, int]] = None,
    total_trials: int = 0,
) -> go.Figure:
    """Bar chart comparing theoretical (25%) vs observed Bell measurement probabilities."""
    outcomes = ["00", "01", "10", "11"]
    theo_probs = [all_probs.get(k, 0.25) * 100.0 for k in outcomes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=outcomes, y=theo_probs, name="Theoretical (25%)",
        marker=dict(color="rgba(56, 189, 248, 0.5)", line=dict(color="#38bdf8", width=1.5)),
    ))

    if observed_counts and total_trials > 0:
        obs_freq = [(observed_counts.get(k, 0) / total_trials) * 100.0 for k in outcomes]
        fig.add_trace(go.Bar(
            x=outcomes, y=obs_freq, name=f"Observed ({total_trials} runs)",
            marker=dict(color="rgba(192, 132, 252, 0.8)", line=dict(color="#c084fc", width=1.5)),
        ))

    fig.update_layout(
        title=dict(text="Bell Measurement Outcomes (|m₀ m₁⟩)", font=dict(color="#e2e8f0", size=13)),
        xaxis=dict(title="Measurement Outcome", tickfont=dict(color="#cbd5e1", size=12), showgrid=False),
        yaxis=dict(title="Probability (%)", tickfont=dict(color="#cbd5e1", size=11),
                   range=[0, 50], gridcolor="rgba(51, 65, 85, 0.4)"),
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0,
                    font=dict(color="#cbd5e1", size=10)),
        margin=dict(l=40, r=20, t=40, b=40),
        height=260,
    )
    return fig


def create_fidelity_history_chart(fidelities: List[float]) -> go.Figure:
    """Line chart tracking teleportation fidelity across multiple trials."""
    fig = go.Figure()
    indices = list(range(1, len(fidelities) + 1))

    fig.add_trace(go.Scatter(
        x=indices, y=fidelities, mode="lines+markers",
        line=dict(color="#10b981", width=2),
        marker=dict(size=4, color="#34d399"),
        name="Trial Fidelity",
    ))
    fig.add_hline(y=1.0, line_dash="dot", line_color="#38bdf8",
                  annotation_text="Ideal (F = 1.0)", annotation_position="bottom right")

    fig.update_layout(
        title=dict(text="Fidelity Across Experimental Trials", font=dict(color="#e2e8f0", size=13)),
        xaxis=dict(title="Trial Number", tickfont=dict(color="#cbd5e1", size=11), showgrid=False),
        yaxis=dict(title="Fidelity F", tickfont=dict(color="#cbd5e1", size=11),
                   range=[0.0, 1.05], gridcolor="rgba(51, 65, 85, 0.4)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        margin=dict(l=40, r=20, t=40, b=40),
        height=260,
    )
    return fig
