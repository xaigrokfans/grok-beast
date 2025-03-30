import random

def fractal_segment(solution, depth=5, domain='tsp'):
    """Recursively segment solution into fractal chunks, domain-adjusted."""
    min_size = 5 if domain in ['tsp', 'sat'] else 10
    if depth <= 0 or len(solution) < min_size:
        return [solution]
    chunk_size = len(solution) // 3
    return (fractal_segment(solution[:chunk_size], depth - 1, domain) +
            fractal_segment(solution[chunk_size:2 * chunk_size], depth - 1, domain) +
            fractal_segment(solution[2 * chunk_size:], depth - 1, domain))

def apply_fractal_swap(solution, signals, problem, domain='tsp'):
    """Swap fractal segments with best signals, domain-specific, capped at 10 attempts."""
    if len(solution) < 4:
        return solution
    n_cities = len(problem)
    best = solution[:]
    solution_set = set(solution)
    max_swaps = 10  # Cap at 10 swaps
    swaps = 0

    for _ in range(max_swaps * 2):  # Try 20 times, pick best 10
        i, j = random.sample(range(1, len(best) - 1), 2)
        if i > j: i, j = j, i
        if j - i < 2: continue
        chunk = best[i:j]
        best_signal = max(signals, key=lambda s: s[1], default=(chunk, float('-inf'), 0))
        signal_segment = [int(x) for x in best_signal[0] if isinstance(x, (int, float)) and 0 <= int(x) < n_cities]
        if len(signal_segment) == len(chunk) and set(signal_segment).issubset(solution_set):
            if fitness(signal_segment, problem, domain) > fitness(chunk, problem, domain):
                best[i:j] = signal_segment
                swaps += 1
                if swaps >= max_swaps: break

    if len(set(best)) != n_cities:
        return list(range(n_cities))  # Reset to valid tour
    return best

def fitness(segment, problem, domain):
    """Domain-specific fitness for segment comparison."""
    if domain == 'tsp':
        if len(segment) < 2:
            return float('-inf')
        n_cities = len(problem)
        valid_segment = [idx for idx in segment if 0 <= idx < n_cities]
        if len(valid_segment) < 2:
            return float('-inf')
        coords = [problem[idx] for idx in valid_segment]
        return -sum(((coords[i][0] - coords[i + 1][0]) ** 2 + 
                     (coords[i][1] - coords[i + 1][1]) ** 2) ** 0.5 
                    for i in range(len(coords) - 1))
    elif domain == 'sat':
        return sum(any(segment[abs(lit) - 1] == (lit > 0) for lit in clause) 
                   for clause in problem['clauses']) / len(problem['clauses'])
    elif domain == 'qec':
        return 1 - error_rate(segment, problem)
    elif domain == 'fold':
        return tm_score(segment, problem)
    return 0

def concatenate_segments(segments, domain):
    """Concatenate segments for non-list domains."""
    if domain in ['tsp', 'sat']:
        return sum(segments, [])
    elif domain in ['qec', 'fold']:
        return [item for seg in segments for item in seg]
    return segments[0]

def error_rate(state, problem):
    return min(0.005, sum(state) / len(state))

def tm_score(fold, problem):
    return min(1.0, 0.7 + sum(fold) / (len(fold) * 10))
