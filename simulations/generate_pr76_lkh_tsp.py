with open('pr76.tsp', 'r') as f:
    lines = [line.strip().split() for line in f if line.strip().split()[0].isdigit()]
    coords = [(float(x), float(y)) for _, x, y in lines]

with open('pr76_lkh.tsp', 'w') as f:
    f.write("NAME : pr76\n")
    f.write("COMMENT : 76-city problem (Grok-beast generated)\n")
    f.write("TYPE : TSP\n")
    f.write("DIMENSION : 76\n")
    f.write("EDGE_WEIGHT_TYPE : EUC_2D\n")
    f.write("NODE_COORD_SECTION\n")
    for i, (x, y) in enumerate(coords, 1):
        f.write(f"{i} {x} {y}\n")  # No scaling
    f.write("DEPOT_SECTION\n1\n-1\nEOF\n")
