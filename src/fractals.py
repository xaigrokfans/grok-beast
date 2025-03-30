# src/fractals.py
def fractal_segment(route, depth=3):
    """Recursively segment route into fractal chunks."""
    if depth <= 0 or len(route) < 5:
        return [route]
    chunk_size = len(route) // 3
    return fractal_segment(route[:chunk_size], depth - 1) + \
           fractal_segment(route[chunk_size:2 * chunk_size], depth - 1) + \
           fractal_segment(route[2 * chunk_size:], depth - 1)

def apply_fractal_swap(route, signals):
    """Swap fractal segments with best signals."""
    segments = fractal_segment(route)
    for i, seg in enumerate(segments):
        best_signal = max(signals, key=lambda s: s[1], default=(seg, 0, 0))
        if best_signal[1] > sum(map(lambda x, y: ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5, 
                                 seg[:-1], seg[1:])):
            segments[i] = best_signal[0]
    return sum(segments, [])
