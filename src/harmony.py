# src/harmony.py
class Harmony:
    def __init__(self):
        self.TR = 1.55  # Target Ratio
        self.cues = {'density': 0, 'cluster': 0, 'scale': 0}

    def update_cues(self, cities, route):
        avg_dist = sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                       for a, b in zip(route[:-1], route[1:])) / len(route)
        self.cues['density'] = avg_dist
        self.cues['scale'] = len(cities)
        self.cues['cluster'] = sum(1 for i in range(len(cities) - 1) 
                                  if min(((cities[i][0] - c[0]) ** 2 + (cities[i][1] - c[1]) ** 2) ** 0.5 
                                         for c in cities) < 30) / len(cities)

    def tune_TR(self):
        if self.cues['density'] < 20:
            self.TR = max(1.3, self.TR - 0.05)  # Dense → shorter legs
        if self.cues['scale'] > 500:
            self.TR = min(1.8, self.TR + 0.05)  # Large → stretch harmony
        return self.TR

    def score_segment(self, segment):
        lengths = [((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 for a, b in zip(segment[:-1], segment[1:])]
        if not lengths: return 0
        ratios = [lengths[i] / lengths[i + 1] for i in range(len(lengths) - 1)]
        return sum(abs(r - self.TR) for r in ratios) / len(ratios) if ratios else 0
