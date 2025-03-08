# src/culture.py
class Culture:
    def __init__(self):
        self.meme_pool = []  # [(strategy, weight)]

    def update(self, strategy, improvement):
        if improvement > 0.1:
            self.meme_pool.append((strategy, min(30, improvement * 10)))
        self.meme_pool = sorted(self.meme_pool, key=lambda x: x[1], reverse=True)[:5]
        for i, (strat, w) in enumerate(self.meme_pool):
            if improvement <= 0 and strat == strategy:
                self.meme_pool[i] = (strat, max(0, w - 5))

    def get_top_memes(self):
        return self.meme_pool[:2]
