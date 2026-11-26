"""Interactive 3D Bloch Sphere visualization using Plotly."""

from typing import Optional
import numpy as np
import plotly.graph_objects as go
from quantum.teleportation import QuantumState


def create_bloch_sphere_figure(
    input_state: QuantumState,
    bob_state: Optional[QuantumState] = None,
) -> go.Figure:
    """Generates a 3D Bloch sphere comparing Alice's input state and Bob's output state."""
    fig = go.Figure()

    # Sphere surface
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    fig.add_trace(go.Surface(
        x=np.outer(np.cos(u), np.sin(v)),
        y=np.outer(np.sin(u), np.sin(v)),
        z=np.outer(np.ones(np.size(u)), np.cos(v)),
        opacity=0.08,
        colorscale=[[0, "#38bdf8"], [1, "#818cf8"]],
        showscale=False,
        hoverinfo="none",
    ))

    # Equator and meridians
    t = np.linspace(0, 2 * np.pi, 100)
    zeros = np.zeros_like(t)
    for x, y, z, dash in [
        (np.cos(t), np.sin(t), zeros, "solid"),
        (np.cos(t), zeros, np.sin(t), "dot"),
        (zeros, np.cos(t), np.sin(t), "dot"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode="lines",
            line=dict(color="rgba(148, 163, 184, 0.3)", width=2, dash=dash),
            hoverinfo="none", showlegend=False,
        ))

    # Coordinate axes and basis labels
    axis_len = 1.25
    for ax_x, ax_y, ax_z in [
        ([-axis_len, axis_len], [0, 0], [0, 0]),
        ([0, 0], [-axis_len, axis_len], [0, 0]),
        ([0, 0], [0, 0], [-axis_len, axis_len]),
    ]:
        fig.add_trace(go.Scatter3d(
            x=ax_x, y=ax_y, z=ax_z, mode="lines",
            line=dict(color="rgba(100, 116, 139, 0.6)", width=3),
            hoverinfo="none", showlegend=False,
        ))

    fig.add_trace(go.Scatter3d(
        x=[0, 0, 1.35, -1.35, 0, 0],
        y=[0, 0, 0, 0, 1.35, -1.35],
        z=[1.35, -1.35, 0, 0, 0, 0],
        mode="text",
        text=["|0⟩", "|1⟩", "|+⟩", "|-⟩", "|+i⟩", "|-i⟩"],
        textposition="middle center",
        textfont=dict(color="#94a3b8", size=13, family="monospace"),
        hoverinfo="none", showlegend=False,
    ))

    # Alice's input state vector
    ax, ay, az = input_state.bloch_coords
    fig.add_trace(go.Scatter3d(
        x=[0, ax], y=[0, ay], z=[0, az],
        mode="lines+markers",
        line=dict(color="#00f0ff", width=8),
        marker=dict(size=[0, 8], color="#00f0ff", symbol="diamond"),
        name="Alice Input |ψ⟩",
        hovertext=f"Alice Input |ψ⟩<br>θ={np.degrees(input_state.theta):.1f}°, φ={np.degrees(input_state.phi):.1f}°",
        hoverinfo="text",
    ))

    # Bob's reconstructed state vector
    if bob_state is not None:
        bx, by, bz = bob_state.bloch_coords
        fig.add_trace(go.Scatter3d(
            x=[0, bx], y=[0, by], z=[0, bz],
            mode="lines+markers",
            line=dict(color="#c084fc", width=5, dash="dash"),
            marker=dict(size=[0, 7], color="#c084fc", symbol="circle"),
            name="Bob Reconstructed |ψ_Bob⟩",
            hovertext=f"Bob Reconstructed |ψ_Bob⟩<br>θ={np.degrees(bob_state.theta):.1f}°, φ={np.degrees(bob_state.phi):.1f}°",
            hoverinfo="text",
        ))

    no_axis = dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False, title="")
    fig.update_layout(
        scene=dict(
            xaxis=no_axis, yaxis=no_axis, zaxis=no_axis,
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            aspectmode="cube",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, b=0, t=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=0.02, xanchor="center", x=0.5,
            font=dict(color="#e2e8f0", size=12),
            bgcolor="rgba(15, 23, 42, 0.7)",
        ),
        height=440,
    )
    return fig
