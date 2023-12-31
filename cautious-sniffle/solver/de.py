import random as rd
import numpy as np

from tqdm import tqdm
from time import time

from .model import Model
from .expression import Expression
from .variables import  BinVariable, IntVariable, RealVariable

class Individual:
    def __init__(self, model: Model) -> None:
        self._current_gen = 1
        self._model = model
        self.mutant_vector: dict[BinVariable | IntVariable | RealVariable, float] = dict()

    def initialize_variables(self):
        self._model.set_random_variables_values()

    def calculate_mutant_vector(
        self,
        generation: int,
        cr: float,
        x_c: dict[BinVariable | IntVariable | RealVariable, float],
        x_best: dict[BinVariable | IntVariable | RealVariable, float],
        x_better: dict[BinVariable | IntVariable | RealVariable, float],
        x_worst: dict[BinVariable | IntVariable | RealVariable, float],
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
        current_variable_values = self._model.variables_values

        self._model.set_variables_values(self.mutant_vector)
        candidate_objective = sum(self._model.objective_values[:-1])

        if candidate_objective < current_objective:
            self._model.set_variables_values(current_variable_values)


class DifferentialEvolutionOptimizer:
    def __init__(
        self,
        model: Model,
        num_individuals: int = 100,
        max_iterations: int = 10000,
        crossover_rate: float = 0.95,
    ) -> None:
        self._model = model

        self.num_individuals = max(5, num_individuals)
        self.max_iterations = max_iterations
        self.crossover_rate = crossover_rate

        p1 = 1
        p2 = rd.uniform(0.75, 1)
        p3 = rd.uniform(0.5, p2)
        p_sum = p1 + p2 + p3

        self.w1 = p1 / p_sum
        self.w2 = p2 / p_sum
        self.w3 = p3 / p_sum

        self._population = [
            Individual(model.copy())
            for _ in tqdm(
                range(self.num_individuals), desc="Creating population", position=0
            )
        ]

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

    def _evaluate_xc(
        self,
        x_best: dict[BinVariable | IntVariable | RealVariable, float],
        x_better: dict[BinVariable | IntVariable | RealVariable, float],
        x_worst: dict[BinVariable | IntVariable | RealVariable, float],
    ):
        def xc(var):
            return (
                self.w1 * (x_best[var] - x_better[var])
                + self.w2 * (x_best[var] - x_worst[var])
                + self.w3 * (x_better[var] - x_worst[var])
            )

        return {var: xc(var) for var in x_best}

    def _determine_best_better_worst(self):
        selected = rd.sample(range(len(self._population)), 3)
        individuals = [self._population[x] for x in selected]
        objectives = [ind._model.objective_values for ind in individuals]
        feasibles = [int(bool(obj[-1] >= 0.000001)) for obj in objectives]

        if sum(feasibles) == 3:
            total_objs = [sum(obj[:-1]) for obj in objectives]
            ids = [0, 1, 2]
            best_idx = total_objs.index(max(total_objs))
            worst_idx = total_objs.index(min(total_objs))
            better_idx = (set(ids) - set([best_idx, worst_idx])).pop()
        elif sum(feasibles) == 2:
            total_objs = [sum(obj[:-1]) for obj in objectives]
            ids = [0, 1, 2]
            worst_idx = feasibles.index(False)
            best_idx = ids[0] if total_objs[ids[0]] > total_objs[ids[0]] else ids[1]
            better_idx = (set(ids) - set([best_idx, worst_idx])).pop()
        elif sum(feasibles) == 1:
            penalty = [obj[-1] for obj in objectives]
            ids = [0, 1, 2]
            best_idx = feasibles.index(True)
            better_idx = ids[0] if penalty[ids[0]] < penalty[ids[0]] else ids[1]
            worst_idx = (set(ids) - set([best_idx, better_idx])).pop()
        else:
            total_objs = [sum(obj[:-1]) for obj in objectives]
            ids = [0, 1, 2]
            best_idx = total_objs.index(max(total_objs))
            worst_idx = total_objs.index(min(total_objs))
            if best_idx == worst_idx:
                better_idx = 1
                worst_idx = 2
            else:
                better_idx = (set(ids) - set([best_idx, worst_idx])).pop()

        x_best = individuals[best_idx]._model.variables_values
        x_better = individuals[better_idx]._model.variables_values
        x_worst = individuals[worst_idx]._model.variables_values

        return x_best, x_better, x_worst

    def optimize(self, tolerance=5):
        start_time = time()
        cr = self.crossover_rate

        for individual in self._population:
            individual.initialize_variables()

        self._evatuate_constraint_violation_penalties()
        for gen in tqdm(range(self.max_iterations), desc="Generation", position=1):
            tolerance = self._calculate_tolerance(tolerance)

            obj_pool = list()
            for individual in tqdm(self._population, desc="Individual", position=0, leave=False):
                obj_values = individual._model.objective_values
                x_best, x_better, x_worst = self._determine_best_better_worst()
                xc = self._evaluate_xc(x_best, x_better, x_worst)
                individual.calculate_mutant_vector(
                    gen, cr, xc, x_best, x_better, x_worst
                )
                individual.update_variables()
                obj_pool.append(obj_values)

            self.evolution_data.append(obj_pool)

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
        self.solution = self._population[best_ind]._model
        return self._population[best_ind]._model
