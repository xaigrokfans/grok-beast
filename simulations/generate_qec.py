with open("quantum_5000.qec", "w") as f:
    f.write("# Simulated Quantum Error Correction Problem\n")
    f.write("# Generated for Grok-beast 2.0 by Grok (xAI), March 20, 2025\n")
    f.write("# 5000 qubits, 25% noise, surface code-like structure\n\n")
    f.write("qubits: 5000\n")
    f.write("noise: 0.25\n")
    f.write("t1: 50e-6\n")
    f.write("gates: 10000\n\n")
    f.write("state: " + "0" * 5000 + "\n\n")
    f.write("stabilizers:\n")
    # X stabilizers (0–2499)
    for i in range(0, 2500, 4):
        f.write(f"{i} {i+1} {i+2} {i+3} X\n")
    # Z stabilizers (2500–4999)
    for i in range(2500, 5000, 4):
        f.write(f"{i} {i+1} {i+2} {i+3} Z\n")
