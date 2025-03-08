# src/chaos.py
import random

class ChaosHandler:
    def __init__(self, noise_level=0.1):
        self.noise_level = noise_level

    def noisy_dist(self, a, b):
        base = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        return base * (1 + random.uniform(-self.noise_level, self.noise_level))

    def robust_signal(self, segment, dist_func):
        lengths = [sum(dist_func(segment[i], segment[i + 1]) for i in range(len(segment) - 1)) 
                  for _ in range(3)]
        return segment, sum(lengths) / 3, min(lengths) / max(lengths)  # Score + consistency

    def chaos_two_opt(self, route, dist_func):
        best = route[:]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, len(best)):
                    if j - i == 1: continue
                    new_route = best[:i] + best[i:j][::-1] + best[j:]
                    gains = [sum(dist_func(best[k], best[k + 1]) for k in range(len(best) - 1)) -
                             sum(dist_func(new_route[k], new_route[k + 1]) for k in range(len(new_route) - 1))
                             for _ in range(3)]
                    if sum(1 for g in gains if g > 0) >= 2:  # 2/3 noise-stable
                        best = new_route
                        improved = True
        return best
