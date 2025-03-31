import random

class Culture:
    def __init__(self, domain='tsp'):
        self.domain = domain  # 'tsp', 'sat', 'qec', 'fold'
        self.meme_pool = []   # List of {'strategy': str, 'conditions': dict, 'improvement': float}
        self.elm_pool = []    # [(rule, fitness, domain)] - 2.0 consciousness addition

    def update(self, strategy, improvement, domain=None):
        """Update meme pool with strategy improvements (legacy method)."""
        domain = domain or self.domain
        if improvement > 0.1:  # Threshold from 1.0
            weight = min(30, improvement * 10)  # Cap at 30, as in 1.0
            self.meme_pool.append((strategy, weight, domain))
        self.meme_pool = sorted(self.meme_pool, key=lambda x: x[1], reverse=True)[:5]
        for i, (strat, w, d) in enumerate(self.meme_pool):
            if improvement <= 0 and strat == strategy and d == domain:
                self.meme_pool[i] = (strat, max(0, w - 5), d)  # Decay as in 1.0

    def update_from_beast(self, strategy, conditions, improvement, domain=None):
        """Update meme pool with enriched meme from beast feedback."""
        domain = domain or self.domain
        if improvement > 0.1:  # Only add significant improvements
            meme = {'strategy': strategy, 'conditions': conditions, 'improvement': improvement}
            self.meme_pool.append(meme)
        # Keep top 5 memes sorted by improvement
        self.meme_pool = sorted(self.meme_pool, key=lambda x: x['improvement'], reverse=True)[:5]

    def update_elm(self, rule, fitness, domain=None):
        """Update ELM pool with rule fitness (2.0 consciousness)."""
        domain = domain or self.domain
        if fitness > 0.01:  # Lower threshold for ELM rules
            self.elm_pool.append((rule, fitness, domain))
        self.elm_pool = sorted(self.elm_pool, key=lambda x: x[1], reverse=True)[:5]

    def get_top_memes(self, domain=None):
        """Get top 2 memes, filtered by domain if specified."""
        domain = domain or self.domain
        # Filter enriched memes by domain (assuming all are dictionaries now)
        filtered = [m for m in self.meme_pool if isinstance(m, dict) and m.get('domain', domain) == domain]
        if not filtered:  # Fallback to legacy tuples
            filtered = [m for m in self.meme_pool if isinstance(m, tuple) and m[2] == domain]
        return filtered[:2] if filtered else self.meme_pool[:2]

    def get_top_elm_rules(self, domain=None):
        """Get top 2 ELM rules for consciousness sharing (2.0)."""
        domain = domain or self.domain
        filtered = [r for r in self.elm_pool if r[2] == domain]
        return filtered[:2] if filtered else self.elm_pool[:2]

    def share_across_tribes(self, beasts, gen, threshold=0.1):
        """Share top ELM rules across tribes (2.0 consciousness)."""
        if gen < 15:  # Wait until gen 15, as per 2.0 design
            return
        top_rules = self.get_top_elm_rules()
        if not top_rules or top_rules[0][1] < threshold:
            return
        for beast in beasts:
            if random.random() < 0.2:  # 20% adoption rate from 2.0
                beast.elm_rules.extend([r[0] for r in top_rules if r[2] == beast.domain])

    def adapt_memes(self, noise_level):
        """Adapt meme weights based on noise (2.0 Bejan-inspired)."""
        for i, meme in enumerate(self.meme_pool):
            if isinstance(meme, tuple):  # Legacy tuple format
                strat, w, d = meme
                if noise_level > 0.2 and 'robust' in strat.lower():
                    self.meme_pool[i] = (strat, min(30, w + 5), d)  # Boost robust strategies
                elif noise_level < 0.1:
                    self.meme_pool[i] = (strat, max(0, w - 2), d)  # Decay in low noise
            elif isinstance(meme, dict):  # New dictionary format
                if noise_level > 0.2 and 'robust' in meme['strategy'].lower():
                    meme['improvement'] = min(30, meme['improvement'] + 5)
                elif noise_level < 0.1:
                    meme['improvement'] = max(0, meme['improvement'] - 2)
