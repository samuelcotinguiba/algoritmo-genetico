from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Item:
    name: Optional[str]
    weight: int
    value: int


class KnapsackProblem:

    def __init__(self, items: List[Item], capacity: int, penalty_factor: float = 10.0):
        self.items = items
        self.capacity = capacity
        self.penalty_factor = penalty_factor

    def evaluate(self, individual: List[int]) -> Tuple[float, int, int]:
        total_weight = 0
        total_value = 0
        for gene, item in zip(individual, self.items):
            if gene:
                total_weight += item.weight
                total_value += item.value

        if total_weight <= self.capacity:
            fitness = float(total_value)
        else:
            fitness = -1e9

        return fitness, total_value, total_weight
