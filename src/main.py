from beast import Beast
from fractals import apply_fractal_swap
from harmony import Harmony
from culture import Culture
from chaos import ChaosHandler
from lkh_wrapper import ChaosLKH
import argparse
import time
import logging
import numpy as np
import sys

def load_problem(file, domain):
    """Load problem data based on domain."""
    if domain == 'tsp':
        with open(file, 'r') as f:
            return [(float(line.split()[1]), float(line.split()[2])) 
                    for line in f if line.strip().split()[0].isdigit()]
    elif domain == 'sat':
        with open(file, 'r') as f:
            lines = [line.strip().split() for line in f if line.strip() and not line.startswith('c')]
            vars = int(lines[0][2])
            clauses = [tuple(int(lit) for lit in line[:-1]) for line in lines[1:]]
            return {'vars': vars, 'clauses': clauses}
    elif domain == 'qec':
        with open(file, 'r') as f:
            qubits = int(f.readline().split(':')[1])
            return {'qubits': qubits, 'state': [0] * qubits}
    elif domain == 'fold':
        with open(file, 'r') as f:
            sequence = ''.join(line.strip() for line in f if not line.startswith('>'))
            return {'sequence': sequence, 'angles': [0.0] * (len(sequence) * 2)}
    raise ValueError(f"Unsupported domain: {domain}")

def format_time(seconds):
    """Convert seconds to HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def main(domain, file, debug=False, logfile=None, verbosity=-1, cultural_signals=False):
    # Map verbosity to levels, -1 means "off"
    level_map = {-1: logging.CRITICAL + 1,  # Higher than CRITICAL (50) disables all
                 0: logging.WARNING,
                 1: logging.INFO,
                 2: logging.DEBUG}
    level = level_map.get(verbosity, logging.CRITICAL + 1)  # Default to WARNING if invalid
    # Set up logging at root level
    logger = logging.getLogger()  # Root logger ("")
    logger.setLevel(level)

    # Only add handlers if logging is enabled (verbosity >= 0)
    if verbosity >= 0:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if specified
        if logfile:
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    # Module-specific loggers
    main_logger = logging.getLogger(__name__)  # "__main__"
    main_logger.debug(f"[Main]Initialized logging with verbosity {verbosity}")

    problem = load_problem(file, domain)
    n_items = len(problem) if domain == 'tsp' else problem.get('vars', problem.get('qubits', len(problem['sequence'])))
    n_tribes = max(10, n_items // 40)
    main_logger.debug(f"[Main]Initialized {n_tribes} tribes for {n_items} items")
    
    dist_matrix = None
    if domain == 'tsp':
        coords = np.array(problem)
        dist_matrix = np.sqrt(
            (coords[:, 0, None] - coords[:, 0])**2 + 
            (coords[:, 1, None] - coords[:, 1])**2
        )
    
    harmony = Harmony(domain=domain)
    culture = Culture(domain=domain)
    chaos = ChaosHandler(noise_level=0, dist_matrix=dist_matrix)
    polish = ChaosLKH(noise_level=0)
    
    tribes = [[Beast('local' if i < 2 else 'global', t, domain, dist_matrix) 
               for i in range(4)] for t in range(n_tribes)]
    best_solution = tribes[0][0].solution[:]
    best_fitness = chaos.fitness(best_solution, problem, domain)
    best_beast = tribes[0][0]

    start_time = time.time()
    #total_gens = 5 if n_items < 100 else 25
    total_gens = 1
    gen_times = []

    for gen in range(total_gens):
        gen_start = time.time()
        all_signals = []
 
        for t, tribe in enumerate(tribes):
            tribe_solutions = []
            for b, beast in enumerate(tribe):
                noisy_problem = chaos.apply_noise(problem, domain)
                main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {b} starting evolve")
                #solution = beast.evolve(noisy_problem, all_signals, culture.get_top_memes(), gen, culture=culture)
                solution = beast.evolve(noisy_problem, all_signals, culture.get_top_memes(), gen, culture=culture, use_cultural_signals=cultural_signals)
                tribe_solutions.append(solution)
                beast.solution = solution[:]
                all_signals.extend(beast.signals)
                main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {b} solution len: {len(solution)}, signals added: {len(beast.signals)}")
            main_logger.info(f"[Main]Gen {gen}, Tribe {t} post-beast, signals total: {len(all_signals)}")
            for beast in tribe:
                if beast.role == 'global':
                    main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {beast.role} entering fractal_swap")
                    beast.solution = apply_fractal_swap(beast.solution, all_signals, problem, domain)
                    main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {beast.role} fractal_swap done")
            if gen % 10 == 0 and gen > 0 and n_items >= 100:
                for beast in tribe:
                    main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {beast.role} entering chaos_two_opt")
                    beast.solution = chaos.chaos_two_opt(beast.solution, problem)
                    main_logger.debug(f"[Main]Gen {gen}, Tribe {t}, Beast {beast.role} chaos_two_opt done")
            culture.share_across_tribes(tribe, gen)
            main_logger.debug(f"[Main]Gen {gen}, Tribe {t} post-tribe ops done")

        harmony.update_cues(problem, tribes[0][0].solution)
        harmony.tune_TR()
        total_fitness = sum(beast.fitness(beast.solution) for t in tribes for beast in t)
        for tribe in tribes:
            for beast in tribe:
                fit = beast.fitness(beast.solution)
                if (domain == 'tsp' and fit < best_fitness) or (domain != 'tsp' and fit > best_fitness):
                    best_fitness = fit
                    best_solution = beast.solution[:]
                    best_beast = beast

        gen_time = time.time() - gen_start
        gen_times.append(gen_time)
        elapsed = time.time() - start_time
        avg_gen_time = sum(gen_times) / len(gen_times)
        remaining_gens = total_gens - (gen + 1)
        est_wait = avg_gen_time * remaining_gens
        print(f"\rGen {gen + 1}/{total_gens} | Elapsed: {format_time(elapsed)} | Est. Wait: {format_time(est_wait)}", end='', flush=True)

    print()
    main_logger.debug(f"[Main]Best solution after evolution: {best_solution[:10]}...")
    polished_solution = polish.polish(best_solution, problem, 1, domain, file.split('/')[-1])
    best_beast.solution = polished_solution[:]
    
    runtime = time.time() - start_time
    flow = harmony.flow_fitness(polished_solution, problem, runtime)
    final_fitness = chaos.fitness(polished_solution, problem, domain)
    print(f"Domain: {domain}")
    print(f"Best fitness: {best_fitness:.4f}")
    print(f"Polished fitness: {final_fitness:.4f}")
    print(f"Flow fitness: {flow:.2f}")
    print(f"Runtime: {runtime:.2f}s")
    return polished_solution

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grok-beast 2.0 Multi-Domain Solver")
    parser.add_argument("--domain", choices=['tsp', 'sat', 'qec', 'fold'], required=True, help="Problem domain")
    parser.add_argument("--file", required=True, help="Path to problem file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging (verbosity=2)")
    parser.add_argument("--logfile", type=str, help="Path to log file for debug output")
    parser.add_argument("--verbosity", type=int, choices=[-1, 0, 1, 2], default=-1, help="Verbosity level: -1=off, 0=minimal, 1=moderate, 2=full")
    parser.add_argument("--cultural-signals", action="store_true", help="Enable cultural signals optimization")
    args = parser.parse_args()
    # If --debug is set, force verbosity to 2 unless explicitly overridden
    verbosity = 2 if args.debug and args.verbosity == 0 else args.verbosity
#    main(args.domain, args.file, args.debug, args.logfile, verbosity)
    main(args.domain, args.file, args.debug, args.logfile, args.verbosity, args.cultural_signals)
