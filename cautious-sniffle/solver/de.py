from __future__ import annotations
from multiprocessing.managers import ListProxy

import random as rd
import numpy as np

from tqdm import tqdm
from time import time
from multiprocessing import Pool, cpu_count

from .model import Model
from .expression import Expression
from .system_utils import RecursionLimiter

class Individual:
    def __init__(self, model: Model) -> None:
        self._current_gen = 1
        self._model = model
        self.mutant_vector: dict[str, float] = dict()

    def initialize_variables(self):
        for var in self._model._vars:
            self._model._vars[var].set_random_value()

    def calculate_mutant_vector(
        self,
        generation: int,
        cr: float,
        x_c: dict[str, float],
        x_best: dict[str, float],
        x_better: dict[str, float],
        x_worst: dict[str, float],
    ):
        self._current_gen = generation
        f1 = rd.uniform(0, 1)
        f2 = rd.uniform(0, 1)
        f3 = rd.uniform(0, 1)

        def mutate(var):
            return (
                x_c[var]
                + f1 * (x_best[var] - x_better[var])
                + f2 * (x_best[var] - x_worst[var])
                + f3 * (x_better[var] - x_worst[var])
            )

        mutant_vector = {var: mutate(var) for var in x_c}
        selected_var = rd.sample(list(mutant_vector.keys()), 1)

        for var in mutant_vector:
            if rd.uniform(0, 1) < cr or var == selected_var:
                self.mutant_vector[var] = mutant_vector[var]

    def update_variables(self):
        current_objective = sum(self._model.objective_values[:-1])
        current_variable_values = self._model.get_variables_values()

        self._model.set_variables_values(self.mutant_vector)
        candidate_objective = sum(self._model.objective_values[:-1])

        if candidate_objective < current_objective:
            self._model.set_variables_values(current_variable_values)


def _evaluate_xc(
    x_best: dict[str, float],
    x_better: dict[str, float],
    x_worst: dict[str, float],
    w1: float,
    w2: float,
    w3: float,
):
    def xc(var):
        return (
            w1 * (x_best[var] - x_better[var])
            + w2 * (x_best[var] - x_worst[var])
            + w3 * (x_better[var] - x_worst[var])
        )

    return {var: xc(var) for var in x_best}


def _determine_best_better_worst(population: ListProxy):
    selected = rd.sample(range(len(population)), 3)
    individuals = [population[x] for x in selected]
    objectives = [ind._model.objective_values for ind in individuals]
    feasibles = [int(obj[-1] >= 0.000001) for obj in objectives]

    if sum(feasibles) == 3:
        total_objs = [sum(obj[:-1]) for obj in objectives]
        ids = [0, 1, 2]
        best_idx = total_objs.index(max(total_objs))
        ids.remove(best_idx)
        worst_idx = total_objs.index(min(total_objs))
        ids.remove(worst_idx)
        better_idx = ids[0]
    elif sum(feasibles) == 2:
        total_objs = [sum(obj[:-1]) for obj in objectives]
        ids = [0, 1, 2]
        worst_idx = feasibles.index(False)
        ids.remove(worst_idx)
        best_idx = ids[0] if total_objs[ids[0]] > total_objs[ids[0]] else ids[1]
        ids.remove(best_idx)
        better_idx = ids[0]
    elif sum(feasibles) == 1:
        penalty = [obj[-1] for obj in objectives]
        ids = [0, 1, 2]
        best_idx = feasibles.index(True)
        ids.remove(best_idx)
        better_idx = ids[0] if penalty[ids[0]] < penalty[ids[0]] else ids[1]
        ids.remove(better_idx)
        worst_idx = ids[0]
    else:
        total_objs = [sum(obj[:-1]) for obj in objectives]
        ids = [0, 1, 2]
        best_idx = total_objs.index(max(total_objs))
        ids.remove(best_idx)
        worst_idx = total_objs.index(min(total_objs))
        if best_idx == worst_idx:
            better_idx = 1
            worst_idx = 2
        else:
            ids.remove(worst_idx)
            better_idx = ids[0]

    x_best = individuals[best_idx]._model.variables_values
    x_better = individuals[better_idx]._model.variables_values
    x_worst = individuals[worst_idx]._model.variables_values

    return x_best, x_better, x_worst


def _compute_step_for_individual(
    population: ListProxy, idx: int, gen: int, cr: float, w1: float, w2: float, w3: float
):
    with RecursionLimiter(1_000_000):
        obj_values = population[idx]._model.objective_values
        x_best, x_better, x_worst = _determine_best_better_worst(population)
        xc = _evaluate_xc(x_best, x_better, x_worst, w1, w2, w3)
        population[idx].calculate_mutant_vector(gen, cr, xc, x_best, x_better, x_worst)
        population[idx].update_variables()

    return obj_values


class DifferentialEvolutionOptimizer:
    def __init__(
        self,
        model: Model,
        population: ListProxy,
        num_individuals: int = 100,
        max_iterations: int = 10000,
        crossover_rate: float = 0.95,
    ) -> None:
        self._population = population
        self._model = model

        self.num_individuals = num_individuals
        self.max_iterations = max_iterations
        self.crossover_rate = crossover_rate

        p1 = 1
        p2 = rd.uniform(0.75, 1)
        p3 = rd.uniform(0.5, p2)
        p_sum = p1 + p2 + p3

        self.w1 = p1 / p_sum
        self.w2 = p2 / p_sum
        self.w3 = p3 / p_sum

        print("Creating population:")
        for _ in tqdm(range(self.num_individuals)):
            population.append(Individual(self._model.copy()))

        self.evolution_data: list[list[list[float]]] = list()
        self.solve_time = None
        self.solution = self._model

    def _evatuate_constraint_violation_penalties(self):
        def cv(individual: Individual):
            def cvj(gj: Expression):
                try:
                    val = gj.value
                except AttributeError:
                    val = gj
                try:
                    ret_val = max(0.0, val)
                except TypeError:
                    ret_val = max(0.0, np.absolute(val))
                return ret_val

            return [cvj(gj) for gj in individual._model._constraints]

        violations = [cv(indi) for indi in self._population]
        transposed_violations = list(map(list, zip(*violations)))
        max_violations = [
            max(constraint_j_viol) for constraint_j_viol in transposed_violations
        ]

        for index in range(self.num_individuals):
            individual_violation = violations[index]
            total_constraints = len(individual_violation)
            penalty = (
                -1
                * sum(
                    [
                        a / b
                        for a, b in zip(individual_violation, max_violations)
                        if b != 0
                    ]
                )
                / total_constraints
            )
            self._population[index]._model.set_constraint_violation_penalty(penalty)

    @staticmethod
    def _calculate_tolerance(tolerance):
        new_tolerance = 0.0001
        if tolerance > 0.0001:
            new_tolerance = tolerance / 1.0168
        return new_tolerance

    def optimize(self, population: ListProxy[Individual], tolerance=5):
        start_time = time()
        cr = self.crossover_rate
        workers = max(cpu_count() - 2, 1)
        for individual in population:
            individual.initialize_variables()

        self._evatuate_constraint_violation_penalties()

        for gen in tqdm(range(self.max_iterations), position=0, desc="Generation"):
            tolerance = self._calculate_tolerance(tolerance)

            obj_values = list()
            with Pool(processes=workers) as pool:
                obj_values = pool.starmap(
                    _compute_step_for_individual,
                    [
                        [population, idx, gen, cr, self.w1, self.w2, self.w3]
                        for idx in range(self.num_individuals)
                    ],
                )

            self.evolution_data.append(obj_values)

            self._evatuate_constraint_violation_penalties()

        best_ind = 0
        best_obj = sum(self._population[best_ind]._model.objective_values)
        for j in range(self.num_individuals):
            obj = self._population[j]._model.objective_values
            if sum(obj) > best_obj:
                best_ind = j
                best_obj = sum(self._population[best_ind]._model.objective_values)

        stop_time = time()
        self.solve_time = stop_time - start_time

        return self._population[best_ind]._model
