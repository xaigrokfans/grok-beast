import subprocess
import tempfile
import os
import logging

class ChaosLKH:
    def __init__(self, noise_level=0):
        self.noise_level = noise_level
        self.lkh_path = '/usr/local/bin/LKH'  # Adjust as needed

    def polish(self, solution, problem_data, trials=1, domain='tsp', problem_name='problem'):
        if domain != 'tsp':
            return solution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsp', delete=False) as tsp_file:
            tsp_file.write(f"NAME: {problem_name}\n")
            tsp_file.write(f"COMMENT: {len(problem_data)}-city problem (Grok-beast generated)\n")
            tsp_file.write("TYPE: TSP\n")
            tsp_file.write(f"DIMENSION: {len(problem_data)}\n")
            tsp_file.write("EDGE_WEIGHT_TYPE: EUC_2D\n")
            tsp_file.write("NODE_COORD_SECTION\n")
            for i, (x, y) in enumerate(problem_data, 1):
                tsp_file.write(f"{i} {x} {y}\n")
            tsp_file.write("EOF\n")
            tsp_file_path = tsp_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.tour', delete=False) as tour_file:
            tour_file.write("TOUR_SECTION\n")
            for idx in solution:
                tour_file.write(f"{idx + 1}\n")
            tour_file.write("-1\nEOF\n")
            tour_file_path = tour_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.par', delete=False) as par_file:
            par_file.write(f"PROBLEM_FILE = {tsp_file_path}\n")
            par_file.write(f"INITIAL_TOUR_FILE = {tour_file_path}\n")
            par_file.write(f"OUTPUT_TOUR_FILE = {tour_file_path}.sol\n")
            par_file.write("RUNS = 1\n")
            par_file.write(f"MAX_TRIALS = {trials}\n")
            par_file.write("MOVE_TYPE = 5\n")
            par_file.write("PATCHING_C = 0\n")
            par_file.write("PATCHING_A = 1\n")
            par_file.write("SEED = 1\n")
            par_file_path = par_file.name

        logger = logging.getLogger(__name__)
        logger.debug(f"Running LKH with: {self.lkh_path} {par_file_path}")
        process = subprocess.run([self.lkh_path, par_file_path], capture_output=True, text=True)
        logger.debug(f"LKH stdout: {process.stdout}")
        logger.debug(f"LKH stderr: {process.stderr}")

        polished_solution = []
        with open(f"{tour_file_path}.sol", 'r') as sol_file:
            lines = sol_file.readlines()
            tour_section = False
            for line in lines:
                line = line.strip()
                if line == "TOUR_SECTION":
                    tour_section = True
                    continue
                if tour_section and line == "-1":
                    break
                if tour_section and line:
                    polished_solution.append(int(line) - 1)

        for f in [tsp_file_path, tour_file_path, par_file_path, f"{tour_file_path}.sol"]:
            try:
                os.remove(f)
            except OSError:
                pass

        return polished_solution
