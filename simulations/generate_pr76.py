with open('pr76.tsp', 'r') as f:
    lines = [line.strip().split() for line in f if line.strip().split()[0].isdigit()]
    coords = [(float(x), float(y)) for _, x, y in lines]
with open('pr76_lkh.tsp', 'w') as f:
    f.write("TYPE: TSP\nDIMENSION: 76\nEDGE_WEIGHT_TYPE: EUC_2D\nNODE_COORD_SECTION\n")
    for i, (x, y) in enumerate(coords, 1):
        f.write(f"{i} {int(x * 1000)} {int(y * 1000)}\n")
    f.write("EOF\n")
