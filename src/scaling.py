class AdaptiveScaler:
    def __init__(self, past_runs=None):
        self.k = 0.1  # Base scaling factor
        self.z = 0.8  # Scaling exponent
        self.te_history = past_runs or {}  # {n_items: te}
        self.domain_adjustments = {
            "tsp": {"k_base": 0.1, "z_base": 0.8, "min_tribes": 6},
            "sat": {"k_base": 0.08, "z_base": 0.85, "min_tribes": 8},
            "qec": {"k_base": 0.12, "z_base": 0.75, "min_tribes": 10},
            "fold": {"k_base": 0.15, "z_base": 0.7, "min_tribes": 4}
        }

    def predict_tribes(self, n_items, domain="tsp"):
        """Predict number of tribes based on problem size and domain."""
        adj = self.domain_adjustments.get(domain, self.domain_adjustments["tsp"])
        tribes = int((self.k + adj["k_base"]) * (n_items ** (self.z + adj["z_base"])))
        return max(1, min(10, n_items // 20))
        '''return max(adj["min_tribes"], tribes)'''

    def tribe_efficiency(self, fitness_improvement, n_beasts, domain="tsp"):
        """Calculate tribe efficiency based on fitness improvement."""
        if domain == "tsp":
            return fitness_improvement / n_beasts / 100  # % length reduction per beast
        elif domain in ["sat", "qec", "fold"]:
            return fitness_improvement / n_beasts / 10   # % fitness gain per beast
        return fitness_improvement / n_beasts

    def tune(self, te_actual, ri_actual, n_items, expected_te, expected_ri, domain="tsp", noise_level=0.25):
        """Tune scaling parameters based on actual vs. expected performance."""
        adj = self.domain_adjustments.get(domain, self.domain_adjustments["tsp"])
        te_diff = te_actual - expected_te
        ri_diff = ri_actual - expected_ri

        # Adjust k for tribe efficiency
        if abs(te_diff) > 0.05:
            self.k += 0.02 * (1 + noise_level) if te_diff < 0 else -0.02 * (1 + noise_level)
            self.k = max(0.05, min(0.2, self.k))  # Clamp k

        # Adjust z for route/fitness improvement
        if abs(ri_diff) > 0.1:
            self.z += 0.05 * (1 + noise_level) if ri_diff < 0 else -0.05 * (1 + noise_level)
            self.z = max(0.5, min(1.0, self.z))  # Clamp z

        self.te_history[(n_items, domain)] = te_actual

    def expected_te(self, n_items, domain="tsp"):
        """Estimate expected tribe efficiency."""
        base_te = 0.02 * (n_items ** -0.2)  # Diminishing returns from 1.0
        if domain == "tsp":
            return base_te
        elif domain == "sat":
            return base_te * 1.2  # SAT slightly higher efficiency
        elif domain == "qec":
            return base_te * 0.8  # QEC lower due to noise
        elif domain == "fold":
            return base_te * 1.5  # Folding higher due to small size
        return base_te

    def expected_ri(self, n_items, domain="tsp"):
        """Estimate expected fitness improvement."""
        base_ri = 10 * (n_items ** 0.5)  # Rough scaling law from 1.0
        if domain == "tsp":
            return base_ri
        elif domain == "sat":
            return base_ri * 0.5  # SAT smaller relative gains
        elif domain == "qec":
            return base_ri * 0.3  # QEC even smaller
        elif domain == "fold":
            return base_ri * 2.0  # Folding larger gains
        return base_ri

    def flow_adjustment(self, noise_level):
        """Bejan-inspired adjustment for flow fitness."""
        return 1 + min(noise_level / 0.15, 1.5)  # Caps at 2.5x for 25% noise
