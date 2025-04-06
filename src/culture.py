import random

class Culture:
    def __init__(self, domain='tsp'):
        self.domain = domain
        self.meme_pool = []

    def update_from_beast(self, strategy, conditions, improvement, domain=None):
        domain = domain or self.domain
        if improvement > 0.1:
            meme = {'strategy': strategy, 'conditions': conditions, 'improvement': improvement}
            self.meme_pool.append(meme)
        self.meme_pool = sorted(self.meme_pool, key=lambda x: x['improvement'], reverse=True)[:5]

    def get_top_memes(self, domain=None):
        domain = domain or self.domain
        filtered = [m for m in self.meme_pool if m.get('domain', domain) == domain]
        return filtered[:2] if filtered else self.meme_pool[:2]

    def share_across_tribes(self, beasts, gen, threshold=0.1):
        if gen < 15:
            return
        top_memes = self.get_top_memes()
        if not top_memes or top_memes[0]['improvement'] < threshold:
            return
        for beast in beasts:
            if random.random() < 0.2:
                pass  # Placeholder for meme application if needed
