# Quantum Teleportation Lab

An interactive Streamlit application using NumPy state vectors to demonstrate the 3-qubit Quantum Teleportation protocol (Bennett et al., 1993).

## Protocol Overview

Alice teleports an unknown single-qubit state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ (on `q0`) to Bob (`q2`) using a shared entangled Bell pair $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$ (`q1, q2`) and two classical bits $(m_0, m_1)$:

1. **Input Preparation:** Prepare $|\psi\rangle$ on `q0` (`RY(θ)` and `P(φ)`).
2. **Entanglement Generation:** Apply `H` on `q1` and `CNOT(q1 → q2)` to create $|\Phi^+\rangle$.
3. **Alice's Bell Analysis:** Apply `CNOT(q0 → q1)` and `H` on `q0`.
4. **Measurement:** Measure `q0` and `q1` to get classical bits $(m_0, m_1)$ (25% probability each).
5. **Classical Communication:** Send $(m_0, m_1)$ to Bob.
6. **Bob's Correction:** Apply $X$ if $m_1 = 1$, then $Z$ if $m_0 = 1$ ($U = Z^{m_0} X^{m_1}$), achieving fidelity $F = 1.0$.

## Project Structure

```text
quantum_teleportation/
├── app.py                      # Streamlit web UI
├── quantum/
│   ├── __init__.py
│   └── teleportation.py        # NumPy 3-qubit state-vector engine
├── visualization/
│   ├── __init__.py
│   ├── bloch_sphere.py         # 3D Bloch sphere (Alice vs Bob)
│   ├── circuit_diagram.py      # 3-qubit circuit schematic
│   └── charts.py               # Outcome probability & fidelity charts
├── tests/
│   └── test_teleportation.py   # Automated unit tests
├── requirements.txt
└── README.md
```

## Setup & Running on Windows

1. Open PowerShell inside this `quantum_teleportation` folder.
2. Activate the virtual environment (or create one with `python -m venv .venv` and install with `pip install -r requirements.txt`):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Run the automated unit tests:
   ```powershell
   python -m unittest discover -s tests -p "test_*.py" -v
   ```
4. Start the Streamlit web app:
   ```powershell
   streamlit run app.py
   ```
