# Generate sat_10000.cnf
import random

def generate_3sat_cnf(vars=10000, clauses=42600, filename="sat_10000.cnf"):
    with open(filename, 'w') as f:
        # Header
        f.write("c Random 3-SAT instance for Grok-beast 2.0\n")
        f.write(f"c {vars} variables, ~{clauses} clauses\n")
        f.write(f"p cnf {vars} {clauses}\n")
        # Clauses
        for _ in range(clauses):
            # Pick 3 unique variables
            lits = random.sample(range(1, vars + 1), 3)
            # Randomly negate each with 50% chance
            clause = [lit if random.random() < 0.5 else -lit for lit in lits]
            f.write(f"{clause[0]} {clause[1]} {clause[2]} 0\n")

# Run in your local dir
generate_3sat_cnf()
