import random
import numpy as np

class ELM:
    def __init__(self, domain="tsp"):
        self.domain = domain  # 'tsp', 'sat', 'qec', 'fold'
        self.rules = []       # List of {'condition': str, 'actions': list, 'fitness': float}
        self.domain_actions = {
            "tsp": ["4-opt", "core swaps"],
            "sat": ["flip", "cluster"],
            "qec": ["parity", "reroute"],
            "fold": ["adjust phi/psi", "cluster cores"]
        }

    def generate_rule(self, beast, gen):
        """Generate a new ELM rule based on beast state and generation."""
        conditions = [
            f"noise > {random.uniform(0.1, 0.3):.1f}",
            f"gen > {gen + random.randint(5, 15)}"
        ]
        actions = random.sample(self.domain_actions[self.domain], k=1)  # Single action for simplicity
        fitness = beast.fitness(beast.solution) if beast.solution else 0
        return {"condition": random.choice(conditions), "actions": actions, "fitness": fitness}

    def evolve(self, population, gen):
        """Evolve ELM rules based on top-performing beasts."""
        top = sorted(population, key=lambda p: p.fitness(p.solution), reverse=True)[:max(1, int(0.1 * len(population)))]
        for beast in top:
            rule = self.generate_rule(beast, gen)
            if rule["fitness"] > 0.01:  # Threshold from prior snippet
                self.rules.append(rule)
        self.rules = sorted(self.rules, key=lambda r: r["fitness"], reverse=True)[:10]  # Keep top 10
        if random.random() < 0.1:  # 10% mutation chance
            self.mutate_rule()

    def mutate_rule(self):
        """Mutate a random rule in the pool."""
        if not self.rules:
            return
        idx = random.randint(0, len(self.rules) - 1)
        rule = self.rules[idx]
        if random.random() < 0.5:  # 50% chance to tweak condition
            thresh = random.uniform(0.1, 0.3) if "noise" in rule["condition"] else random.randint(5, 15)
            rule["condition"] = f"noise > {thresh:.1f}" if "noise" in rule["condition"] else f"gen > {thresh}"
        else:  # 50% chance to tweak actions
            rule["actions"] = random.sample(self.domain_actions[self.domain], k=1)
        self.rules[idx] = rule

    def apply_rules(self, beast, gen, noise_level):
        """Apply applicable ELM rules to a beast."""
        for rule in self.rules:
            if self.check_condition(rule["condition"], gen, noise_level):
                beast.execute_action(rule["actions"], beast.problem if hasattr(beast, "problem") else None)

    def check_condition(self, condition, gen, noise_level):
        """Evaluate rule condition."""
        if "noise >" in condition:
            thresh = float(condition.split(">")[1])
            return noise_level > thresh
        elif "gen >" in condition:
            thresh = int(condition.split(">")[1])
            return gen > thresh
        return False  # Default fail-safe

    def get_top_rules(self, n=2):
        """Return top N rules by fitness."""
        return sorted(self.rules, key=lambda r: r["fitness"], reverse=True)[:n]
