import random
import time
from culture import Culture
from harmony import Harmony
from chaos import ChaosHandler
from lkh_wrapper import ChaosLKH
from beast import Beast

class GrokBeast:
    """Manages the evolutionary process for solving problems."""
    def __init__(self, problem, pop_size, num_generations, tribes=1, **kwargs):
        self.problem = problem
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.tribes = tribes
        self.population = [
            [Beast(problem, 'local' if i < 2 else 'global', t) for i in range(pop_size // tribes)]
            for t in range(tribes)
        ]
        self.culture = kwargs.get('culture', Culture(problem.domain))
        self.harmony = kwargs.get('harmony', Harmony(problem.domain))
        self.chaos = kwargs.get('chaos', ChaosHandler(noise_level=kwargs.get('noise_level', 0.25)))
        self.polish = kwargs.get('polish', ChaosLKH(noise_level=0))
        self.use_cultural_signals = kwargs.get('use_cultural_signals', False)

    def select_parents(self, tribe):
        """Select parents using tournament selection."""
        tournament_size = 3
        parents = []
        for _ in range(2):
            candidates = random.sample(tribe, min(tournament_size, len(tribe)))
            winner = max(candidates, key=lambda b: b.fitness())
            parents.append(winner)
        return parents

    def run(self):
        """Execute the evolutionary process."""
        start_time = time.time()
        for gen in range(self.num_generations):
            all_signals = []
            for tribe in self.population:
                for beast in tribe:
                    if gen > 0:
                        parents = self.select_parents(tribe)
                        beast.solution = self.problem.crossover(parents[0].solution, parents[1].solution)
                        beast.solution = self.problem.mutate(beast.solution)
                    if self.use_cultural_signals and gen >= 5:
                        memes = self.culture.get_top_memes()
                        if memes:
                            state = self.problem.evaluate_state(beast.solution)
                            meme = self.select_meme(memes, state)
                            if meme:
                                beast.solution = self.problem.apply_strategy(beast.solution, meme['strategy'])
                    signals = self.problem.extract_signals(beast.solution)
                    all_signals.extend(signals)
                for beast in tribe:
                    if beast.role == 'global' and gen % 2 == 0:
                        beast.solution = self.problem.apply_fractal_swap(beast.solution, all_signals)
                    if gen % 10 == 0 and gen > 0 and len(self.problem.data) >= 100:
                        beast.solution = self.chaos.chaos_two_opt(beast.solution, self.problem.data)
                self.culture.share_across_tribes(tribe, gen)
            self.harmony.update_cues(self.problem.data, self.population[0][0].solution)
            self.harmony.tune_TR()
        best_beast = max([b for tribe in self.population for b in tribe], key=lambda b: b.fitness())
        polished_solution = self.polish.polish(best_beast.solution, self.problem.data, 1, self.problem.domain, "problem")
        best_beast.solution = polished_solution
        runtime = time.time() - start_time
        return best_beast.solution, runtime

    def select_meme(self, memes, state):
        """Select the best meme based on the current state."""
        best_meme, best_score = None, -1
        for meme in memes:
            score = sum(1 for k, v in meme['conditions'].items() if state.get(k) == v)
            if score > best_score:
                best_score = score
                best_meme = meme
        return best_meme
