# src/main.py
from beast import Beast
from fractals import apply_fractal_swap
from harmony import Harmony
from scaling import AdaptiveScaler
from culture import Culture
from chaos import ChaosHandler
from lkh_wrapper import ChaosLKH
import argparse

def load_tsp(file):
    # Simplified—assumes x, y coords in file
    with open(file, 'r') as f:
        return [(float(line.split()[1]), float(line.split()[2])) 
                for line in f if line.strip().split()[0].isdigit()]

def main(tsp_file):
    cities = load_tsp(tsp_file)
    n_cities = len(cities)
    scaler = AdaptiveScaler()
    n_tribes = scaler.predict_tribes(n_cities)
    harmony = Harmony()
    culture = Culture()
    chaos = ChaosHandler()
    lkh = ChaosLKH()

    tribes = [[Beast('local' if i < 2 else 'global', t) for i in range(4)] 
              for t in range(n_tribes)]
    best_route = None
    best_length = float('inf')

    for gen in range(25):
        all_signals = []
        for tribe in tribes:
            tribe_routes = []
            for beast in tribe:
                route = beast.evolve(cities, all_signals, culture.get_top_memes())
                tribe_routes.append(route)
                all_signals.extend(beast.signals)
            # Symbiosis: Local feeds Global
            for i, beast in enumerate(tribe):
                if beast.role == 'global':
                    beast.route = apply_fractal_swap(beast.route, 
                                                    [s for r in tribe_routes[:2] for s in Beast().extract_segments(r)])
            # Feedback, bursts, etc. (simplified)
            if gen % 5 == 0 and gen > 0:
                for beast in tribe:
                    beast.route = chaos.chaos_two_opt(beast.route, chaos.noisy_dist)

        harmony.update_cues(cities, tribes[0][0].route)
        harmony.tune_TR()
        te = scaler.tribe_efficiency(sum(b.route_length(b.route) for t in tribes for b in t) / (n_tribes * 4), n_tribes * 4)
        scaler.tune(te, 100, n_cities, scaler.expected_te(n_cities), scaler.expected_ri(n_cities))

    # Polish best route
    best_route = min((b.route for t in tribes for b in t), 
                     key=lambda r: chaos.noisy_dist(r[0], r[-1]))
    best_route = lkh.polish(best_route, cities, int(0.5 * n_cities))
    print(f"Best length: {Beast().route_length(best_route):.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grok-beast 1.0 TSP Solver")
    parser.add_argument("--tsp", required=True, help="Path to TSP file")
    args = parser.parse_args()
    main(args.tsp)
