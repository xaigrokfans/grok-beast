# src/beast.py
class Beast:
    def __init__(self, role='local', tribe_id=0):
        self.role = role  # 'local' (clusters) or 'global' (linking)
        self.tribe_id = tribe_id
        self.route = []
        self.instincts = {'2-opt': 0.5, 'cluster': 0.2, 'nn': 0.3}  # Scale-tuned weights
        self.signals = []  # [(segment, score, epigenetic_tag)]
        self.epigenetic_tags = {}  # {segment: weight}

    def instinct_seed(self, cities):
        from random import choice
        if choice([True, False]):  # 50% 2-opt
            route = self.nearest_neighbor(cities[:])
            return self.two_opt(route)
        return self.cluster_first(cities[:])  # 20% chance

    def nearest_neighbor(self, cities):
        route = [cities.pop(0)]
        while cities:
            last = route[-1]
            next_city = min(cities, key=lambda c: self.dist(last, c))
            route.append(next_city)
            cities.remove(next_city)
        return route

    def two_opt(self, route):
        best = route[:]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, len(best)):
                    if j - i == 1: continue
                    new_route = best[:i] + best[i:j][::-1] + best[j:]
                    if self.route_length(new_route) < self.route_length(best):
                        best = new_route
                        improved = True
        return best

    def cluster_first(self, cities):
        # Simplified: group 10% into mini-tours
        cluster_size = max(1, len(cities) // 10)
        clusters = [cities[i:i + cluster_size] for i in range(0, len(cities), cluster_size)]
        return sum([self.nearest_neighbor(c) for c in clusters], [])

    def fractal_swap(self, route, signals):
        # Depth 3 fractal: split into 3 levels, swap best signal
        chunk_size = len(route) // 3
        for i in range(0, len(route), chunk_size):
            chunk = route[i:i + chunk_size]
            best_signal = max(signals, key=lambda s: s[1], default=(chunk, 0, 0))
            if best_signal[1] > self.route_length(chunk):
                route[i:i + chunk_size] = best_signal[0]
        return route

    def evolve(self, cities, signals, memes):
        self.route = self.instinct_seed(cities)
        self.apply_memes(memes)
        self.signals = [(s, self.route_length(s), self.epigenetic_tags.get(tuple(s), 0)) 
                        for s in self.extract_segments(self.route)]
        return self.fractal_swap(self.route, signals)

    def apply_memes(self, memes):
        # Apply top meme (e.g., adjust TR or instinct weights)
        if memes and memes[0][1] > 0.1:  # Weight > 0.1
            if '2-opt' in memes[0][0]:
                self.instincts['2-opt'] += 0.1

    def dist(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def route_length(self, route):
        return sum(self.dist(route[i], route[i + 1]) for i in range(len(route) - 1)) + \
               self.dist(route[-1], route[0])

    def extract_segments(self, route):
        # Extract 5-city chunks for signals
        return [route[i:i + 5] for i in range(0, len(route) - 4)]
