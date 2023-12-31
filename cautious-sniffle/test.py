import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from time import time
from pprint import pprint

from solver import *

PLOT = False
## CONFIGURAÇÕES PARA SOLVERS
ENABLE_PSO = True
ENABLE_DE = True

PSO_SWARM = 1_000
DE_POPULATION = 1_000

PSO_ITERATIONS = 10_000
DE_ITERATIONS = 10_000


def create_test_model():
    start_time = time()
    model = Model()

    x = model.create_real_variable("x", lb=-100, ub=100)
    y = model.create_integer_variable("y", lb=-100, ub=100)

    x.set_value(75)
    y.set_value(75)

    hiperboloide = 12 * x + y**2 - 120
    print(f"Objective:\n\t{hiperboloide}")
    print(f"\nExpected solution:\n\tX={x.value}\n\tY={y.value}")
    print(f"\nExpected objective value:\n\t{hiperboloide.value}")
    model.set_objective(hiperboloide)

    restricoes_caixa = [
        50 - x,
        50 - y,
        x - 75,
        y - 75,
    ]
    model.insert_lt_zero_constraints(restricoes_caixa)
    print("\nConstraints:\n\t0<=X<=10\n\t0<=Y<=10")
    end_time = time()

    return model, (end_time - start_time)


if __name__ == "__main__":
    model, gen_time = create_test_model()

    print("\nModel Statistics:")
    print(f"{len(model._variables)} variables")
    print(f"{len(model._constraints)} constraints")
    print(f"Created in {gen_time} seconds\n")

    if ENABLE_DE:
        print("\nDE Solution:")
        de = DifferentialEvolutionOptimizer(
            model,
            num_individuals=DE_POPULATION,
            max_iterations=DE_ITERATIONS,
        )
        de.optimize()
        print("With costs:")
        pprint(de.solution.objective_values)
        print(f"In {de.solve_time} seconds\n")
        print("Solution variables:")
        pprint(de.solution.get_variables_values())

        ## DE METRICS
        if PLOT:
            evolution_data = de.evolution_data
            print(evolution_data)
            objectives = [[val[0] for val in it] for it in evolution_data]
            penalties = [[val[1] for val in it] for it in evolution_data]

            for data in objectives:
                data.sort()
            for data in penalties:
                data.sort()

            objectives = list(map(list, zip(*objectives)))
            penalties = list(map(list, zip(*penalties)))

            objectives = np.array(objectives)
            min_value = objectives.min()
            max_value = objectives.max()
            objectives = (objectives - min_value) / (max_value - min_value)

            penalties = np.array(penalties)
            min_value = penalties.min()
            max_value = penalties.max()
            penalties = (penalties - min_value) / (max_value - min_value)

            objs_evo = sns.heatmap(objectives)
            plt.show()

            pen_evo = sns.heatmap(penalties)
            plt.show()

    if ENABLE_PSO:
        print("\nPSO Solution:")
        pso = ParticleSwarmOptimizer(
            model,
            num_particles=PSO_SWARM,
            max_iterations=PSO_ITERATIONS,
        )
        pso.optimize()
        print("With costs:")
        pprint(pso.solution.objective_values)
        print(f"In {pso.solve_time} seconds\n")
        print("Solution variables:")
        pprint(pso.solution.get_variables_values())

        ## PSO METRICS
        if PLOT:
            evolution_data = pso.evolution_data
            objectives = [[val[0] for val in it] for it in evolution_data]
            penalties = [[val[1] for val in it] for it in evolution_data]

            for data in objectives:
                data.sort()
            for data in penalties:
                data.sort()

            objectives = list(map(list, zip(*objectives)))
            penalties = list(map(list, zip(*penalties)))

            objectives = np.array(objectives)
            min_value = objectives.min()
            max_value = objectives.max()
            objectives = (objectives - min_value) / (max_value - min_value)

            penalties = np.array(penalties)
            min_value = penalties.min()
            max_value = penalties.max()
            penalties = (penalties - min_value) / (max_value - min_value)

            objs_evo = sns.heatmap(objectives)
            plt.show()

            pen_evo = sns.heatmap(penalties)
            plt.show()
