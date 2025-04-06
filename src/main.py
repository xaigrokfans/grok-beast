import argparse
import logging
import sys
from problem import TSPProblem
from grok_beast import GrokBeast

def load_problem(file, domain):
    """Load problem data from file."""
    if domain == 'tsp':
        with open(file, 'r') as f:
            return [(float(line.split()[1]), float(line.split()[2]))
                    for line in f if line.strip().split()[0].isdigit()]
    raise ValueError(f"Unsupported domain: {domain}")

def main(domain, file, debug=False, logfile=None, verbosity=-1, cultural_signals=False):
    level_map = {-1: logging.CRITICAL + 1, 0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    level = level_map.get(verbosity, logging.CRITICAL + 1)
    logger = logging.getLogger()
    logger.setLevel(level)
    if verbosity >= 0:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if logfile:
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    data = load_problem(file, domain)
    if domain == 'tsp':
        problem = TSPProblem(data)
    else:
        raise NotImplementedError(f"Domain {domain} not yet implemented")

    n_items = len(data)
    n_tribes = max(10, n_items // 40)
    grok_beast = GrokBeast(
        problem=problem,
        pop_size=n_tribes * 4,
        #num_generations=25 if n_items >= 100 else 5,
        num_generations=3,
        tribes=n_tribes,
        use_cultural_signals=cultural_signals
    )
    best_solution, runtime = grok_beast.run()

    final_fitness = problem.evaluate_fitness(best_solution)
    flow = grok_beast.harmony.flow_fitness(best_solution, problem.data, runtime)
    print(f"Domain: {domain}")
    print(f"Polished fitness: {final_fitness:.4f}")
    print(f"Flow fitness: {flow:.2f}")
    print(f"Runtime: {runtime:.2f}s")
    return best_solution

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grok-beast 2.0 Multi-Domain Solver")
    parser.add_argument("--domain", choices=['tsp', 'sat', 'qec', 'fold'], required=True, help="Problem domain")
    parser.add_argument("--file", required=True, help="Path to problem file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging (verbosity=2)")
    parser.add_argument("--logfile", type=str, help="Path to log file for debug output")
    parser.add_argument("--verbosity", type=int, choices=[-1, 0, 1, 2], default=-1, help="Verbosity level")
    parser.add_argument("--cultural-signals", action="store_true", help="Enable cultural signals")
    args = parser.parse_args()
    verbosity = 2 if args.debug else args.verbosity
    main(args.domain, args.file, args.debug, args.logfile, verbosity, args.cultural_signals)
