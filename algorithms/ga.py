

import random
import time
from typing import List, Tuple, Optional
from problem.problem import KnapsackProblem


class GeneticAlgorithm:

    def __init__(
        self,
        problem: KnapsackProblem,
        pop_size: int = 100,
        generations: int = 200,
        mutation_rate: float = 0.01,
        crossover_rate: float = 0.8,
        tournament_size: int = 3,
        elitism: bool = True,
    ) -> None:
        self.problem = problem
        self.pop_size = int(pop_size)
        self.generations = int(generations)
        self.mutation_rate = float(mutation_rate)
        self.crossover_rate = float(crossover_rate)
        self.tournament_size = int(tournament_size)
        self.elitism = bool(elitism)

    def _random_individual(self) -> List[int]:
        return [random.randint(0, 1) for _ in range(len(self.problem.items))]

    def _repair(self, individual: List[int]) -> None:
        items = self.problem.items
        capacity = self.problem.capacity
        total_weight = sum(items[i].weight for i, bit in enumerate(individual) if bit)

        while total_weight > capacity:
            sel = [i for i, bit in enumerate(individual) if bit]
            if not sel:
                break
            # find item with minimal value/weight ratio
            worst_idx = min(sel, key=lambda i: items[i].value / items[i].weight if items[i].weight > 0 else float('inf'))
            individual[worst_idx] = 0
            total_weight -= items[worst_idx].weight

    def initialize_population(self) -> List[List[int]]:
        pop = [self._random_individual() for _ in range(self.pop_size)]
        for ind in pop:
            self._repair(ind)
        return pop

    def fitness(self, individual: List[int]) -> float:
        fit, _, _ = self.problem.evaluate(individual)
        return fit

    def _tournament_pick(self, population: List[List[int]]) -> List[int]:
        best = random.choice(population)
        best_score = self.fitness(best)
        for _ in range(self.tournament_size - 1):
            challenger = random.choice(population)
            score = self.fitness(challenger)
            if score > best_score:
                best = challenger
                best_score = score
        return best

    def _crossover(self, a: List[int], b: List[int]) -> Tuple[List[int], List[int], bool]:
        if random.random() > self.crossover_rate or len(a) < 2:
            return a[:], b[:], False
        point = random.randrange(1, len(a))
        return a[:point] + b[point:], b[:point] + a[point:], True

    def _mutate(self, individual: List[int]) -> int:
        flips = 0
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                individual[i] = 1 - individual[i]
                flips += 1
        return flips

    def evolve(
        self,
        record_history: bool = False,
        max_time: Optional[float] = None,
        show_progress: bool = False,
    stable_limit: Optional[int] = 15,
    ) -> Tuple[List[int], int, int]:
        population = self.initialize_population()
        best_individual: Optional[List[int]] = None
        best_fitness = float("-inf")

        history = []
        start_time = time.perf_counter()

        gen = 0
        stable_count = 0
        prev_best_value = None

        # If stable_limit is provided and positive, allow potentially unlimited runs
        use_stable = stable_limit is not None and stable_limit > 0

        while True:
            if not use_stable and gen >= self.generations:
                break

            elapsed_since_start = time.perf_counter() - start_time
            if show_progress:
                bf = f"{best_fitness:.2f}" if best_fitness != float("-inf") else "-"
                print(f"\rGeração {gen+1}/{self.generations} — decorrido: {elapsed_since_start:.2f}s — melhor: {bf}", end="", flush=True)

            if max_time is not None and elapsed_since_start >= max_time:
                break

            gen_mutations = 0
            gen_crossovers = 0

            fitnesses = [self.fitness(ind) for ind in population]
            avg_fitness = sum(fitnesses) / len(fitnesses)

            improved = False
            for ind, f in zip(population, fitnesses):
                if f > best_fitness:
                    best_fitness, best_individual, improved = f, ind[:], True

            new_pop: List[List[int]] = []
            if self.elitism and best_individual is not None:
                elite = best_individual[:]
                self._repair(elite)
                new_pop.append(elite)

            while len(new_pop) < self.pop_size:
                p1, p2 = self._tournament_pick(population), self._tournament_pick(population)
                c1, c2, did_cross = self._crossover(p1, p2)
                gen_crossovers += did_cross
                gen_mutations += self._mutate(c1) + self._mutate(c2)
                
                self._repair(c1)
                new_pop.append(c1)
                if len(new_pop) < self.pop_size:
                    self._repair(c2)
                    new_pop.append(c2)

            # stability tracking based on best VALUE (not fitness)
            best_value_now = self.problem.evaluate(best_individual)[1] if best_individual else 0
            
            if prev_best_value is None:
                prev_best_value, stable_count = best_value_now, 0
            elif best_value_now == prev_best_value and not improved:
                stable_count += 1
            elif best_value_now != prev_best_value:
                prev_best_value, stable_count = best_value_now, 0

            if record_history:
                _, best_value, best_weight = self.problem.evaluate(best_individual) if best_individual else (0, 0, 0)
                history.append({
                    "gen": gen,
                    "best_fitness": best_fitness,
                    "avg_fitness": avg_fitness,
                    "mutations": gen_mutations,
                    "crossovers": gen_crossovers,
                    "best_value": best_value,
                    "best_weight": best_weight,
                    "elapsed": time.perf_counter() - start_time,
                })

            population = new_pop
            gen += 1

            if use_stable and stable_count >= stable_limit:
                break

        best_individual = best_individual or [0] * len(self.problem.items)
        _, total_value, total_weight = self.problem.evaluate(best_individual)
        self.history = history if record_history else []
        
        if show_progress:
            print()

        return best_individual, total_value, total_weight

