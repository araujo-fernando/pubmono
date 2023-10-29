from __future__ import annotations

import random as rd
import numpy as np

from copy import deepcopy
from tqdm import tqdm
from time import time

from model import Model
from expression import Expression


class Particle:
    def __init__(self, model: Model, c1: float = 2, r1: float = None) -> None:
        self._current_iter = 1
        self._model = model.copy()
        self._best_pos = self._model.variables_values
        self._best_pos_obj = sum(self.objective_values)

        if r1 is None:
            self.r1 = rd.uniform(0, 1)
        else:
            self.r1 = np.clip(r1, 0, 1)

        self.c1 = c1
        self.variables_speed: dict[str, float] = dict()

    @property
    def objective_values(self) -> list[float]:
        self._model.set_constraint_violation_penalty(
            self._evaluate_constraint_penalties(self._current_iter)
        )
        return self._model.objective_values

    @property
    def Pbest(self) -> dict[str, float]:
        # p_best
        return deepcopy(self._best_pos)

    @property
    def Pbest_obj(self):
        return self._best_pos_obj

    def _evaluate_constraint_penalties(
        self, iter: int, c: float = 0.5, alpha=2, a=150, b=10
    ) -> float:
        Ci = (c * iter) ** alpha

        def qj(x: Expression) -> float:
            try:
                val = x.value
            except AttributeError:
                val = x
            try:
                ret_val = max(0.0, val)
            except TypeError:
                ret_val = max(0.0, np.absolute(val))
            return ret_val

        def phi(qj) -> float:
            try:
                val = a * (1 - (1 / np.exp(qj))) + b
            except RuntimeWarning:
                val = 10 ** 10
            return val

        def gamma(qj) -> float:
            return 1 if qj <= 1 else 2

        def penalty(constraint: Expression):
            viol = qj(constraint)
            return phi(viol) * (viol ** gamma(viol))

        total_penalty = -1* Ci * sum(
            penalty(constraint) for constraint in self._model._constraints
        )

        return total_penalty

    def _update_best_position(self, iter=0):
        current_obj = sum(self.objective_values)
        self._current_iter = iter
        if current_obj > self._best_pos_obj:
            self._best_pos_obj = current_obj
            self._best_pos = self._model.variables_values

    def initialize_variables_and_speeds(self):
        for var in self._model._vars:
            self._model._vars[var].set_random_value()
            self.variables_speed[var] = 0.0

        self._update_best_position()

    def update_variables(self, var_values: dict[str, float], iter=0):
        self._model.set_variables_values(var_values)
        self._update_best_position(iter=iter)

    def update_variables_speed(self, r2, c2, theta, Gbest):
        Pbest = self.Pbest
        v = self.variables_speed
        x = self._model.variables_values
        r1 = self.r1
        c1 = self.c1

        def compute_speed(var: str):
            return (
                theta * v[var]
                + c1 * r1 * (Pbest[var] - x[var])
                + c2 * r2 * (Gbest[var] - x[var])
            )

        self.variables_speed = {var: compute_speed(var) for var in x}

    def update_variables_speed_and_variables(self, r2, c2, theta, Gbest, iter=0):
        Pbest = self.Pbest
        v = self.variables_speed
        x = self._model.variables_values
        r1 = self.r1
        c1 = self.c1

        def compute_speed(var: str):
            return (
                theta * v[var]
                + c1 * r1 * (Pbest[var] - x[var])
                + c2 * r2 * (Gbest[var] - x[var])
            )

        new_v = {var: compute_speed(var) for var in x}
        new_x = {var: x[var] + new_v[var] for var in x}

        self.update_variables(new_x, iter)
        self.variables_speed = new_v


class ParticleSwarmOptimizer:
    def __init__(
        self,
        model: Model,
        num_particles,
        max_iterations,
        **kwargs,
    ) -> None:
        """


        :param model: Model to be solved
        :type model: Model
        :param num_particles: number of particles to be created, defaults to 100
        :type num_particles: int, optional
        :param max_iterations: maximum number of iterations, defaults to 10_000
        :type max_iterations: int, optional
        :param theta_max: max inertia, defaults to 0.9
        :type theta_max: float, optional
        :param theta_min: min inertia, defaults to 0.4
        :type theta_min: float, optional
        :param c2: social learning rate, defaults to 2
        :type c2: float, optional
        :param r2: learning rate weight, defaults to None
        :type r2: float, optional
        """
        self.model = model

        self.num_particles = num_particles
        self.theta_max = kwargs.get("theta_max", 0.9)
        self.theta_min = kwargs.get("theta_min", 0.4)
        self.max_iterations = max_iterations
        self.c2 = kwargs.get("c2", 2)

        r2 = kwargs.get("r2", None)
        if r2 is None:
            self.r2 = rd.uniform(0, 1)
        else:
            self.r2 = np.clip(r2, 0, 1)

        self._particles = [Particle(self.model) for _ in range(self.num_particles)]
        
        self.evolution_data: list[list[list[float]]] = list()
        self.solve_time = None
        self.solution = self.optimize()


    def optimize(self, use_convergence_criteria: bool = False):
        start_time = time()
        r2 = self.r2
        c2 = self.c2
        theta_max = self.theta_max
        theta_min = self.theta_min
        it_max = self.max_iterations

        for particle in self._particles:
            particle.initialize_variables_and_speeds()

        best_particle = 0
        Gbest_obj = self._particles[best_particle].Pbest_obj
        for it in tqdm(range(it_max)):
            Gbest_pos = self._particles[best_particle].Pbest
            Gbest_obj = sum(self._particles[best_particle].objective_values)
            obj_pool = list()
            for j in range(self.num_particles):
                p = self._particles[j]
                objectives = p.objective_values
                obj_pool.append(objectives)
                obj = sum(objectives)
                if obj > Gbest_obj:
                    best_particle = j
                    Gbest_obj = obj
                    Gbest_pos = self._particles[best_particle].Pbest

            theta = theta_max - (theta_max - theta_min) / it_max * it
            for j in range(self.num_particles):
                p = self._particles[j]
                p.update_variables_speed_and_variables(r2, c2, theta, Gbest_pos, it)
            
            self.evolution_data.append(obj_pool) 
            if use_convergence_criteria:
                if self._has_converged(obj_pool):
                    break

        for j in range(self.num_particles):
            p = self._particles[j]
            if sum(p.objective_values) > Gbest_obj:
                best_particle = j
        solution = self._particles[best_particle]._model
        stop_time = time()
        self.solve_time = stop_time - start_time
        
        return solution

    def _has_converged(self, objectives) -> bool:
        objs = [sum(val) for val in objectives]
        min_obj = min(objs)
        denom = max(objs) - min_obj
        if denom == 0:
            return True

        norm_obj = [(val - min_obj) / denom for val in objs]

        for val in norm_obj:
            if val > 0.000001:
                return False

        return True
