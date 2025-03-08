# src/scaling.py
class AdaptiveScaler:
    def __init__(self, past_runs=None):
        self.k = 0.1
        self.z = 0.8
        self.te_history = past_runs or {}  # {n_cities: te}

    def predict_tribes(self, n_cities):
        tribes = int(self.k * (n_cities ** self.z))
        return max(6, tribes)

    def tribe_efficiency(self, route_improvement, n_beasts):
        return route_improvement / n_beasts / 100  # % improvement per beast

    def tune(self, te_actual, ri_actual, n_cities, expected_te, expected_ri):
        if abs(te_actual - expected_te) > 0.05:
            self.k += 0.02 if te_actual < expected_te else -0.02
        if abs(ri_actual - expected_ri) > 0.1:
            self.z += 0.05 if ri_actual < expected_ri else -0.05
        self.te_history[n_cities] = te_actual

    def expected_te(self, n_cities):
        return 0.02 * (n_cities ** -0.2)  # Diminishing returns

    def expected_ri(self, n_cities):
        return 10 * (n_cities ** 0.5)  # Rough scaling law
