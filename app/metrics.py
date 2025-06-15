
"""Simple in-memory usage/cost tracker."""
from collections import defaultdict

PRICE_PER_1K = {
    "gpt-4o": 0.01,          # placeholder
    "gpt-4o-mini": 0.005
}

class UsageMeter:
    def __init__(self):
        self.totals = defaultdict(lambda: {"tokens": 0, "cost": 0.0})

    def add(self, model: str, tokens: int):
        price = PRICE_PER_1K.get(model, 0.0)
        cost = tokens/1000 * price
        self.totals[model]["tokens"] += tokens
        self.totals[model]["cost"] += cost

    def snapshot(self):
        return self.totals

meter = UsageMeter()
