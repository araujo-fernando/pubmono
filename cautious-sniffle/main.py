import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pprint import pprint

from solver import *

PLOT = False
DATA_PATH = "data/elfa"
## CONFIGURAÇÕES PARA SOLVERS
ENABLE_PSO = True
ENABLE_DE = True

PSO_SWARM = 2
DE_POPULATION = 2

PSO_ITERATIONS = 3
DE_ITERATIONS = 3
## CONFIGURAÇÕES PARA MONTAGEM DO PROBLEMA
T = 60

filtro_skus_elfa = ["NUTRICAO", "MATERIAIS", "GENERICO", "ESPECIALIDADES", "SIMILAR"]

if __name__ == "__main__":
    if DATA_PATH:
        model, gen_time = assemble_model_from_data(
            DATA_PATH, "Fornecedor", "Cliente", T, filtro_skus_elfa[0:1]
        )
    else:
        model, gen_time = assemble_model(10, T)

    print("\nModel Statistics:")
    print(f"{len(model._variables)} variables")
    print(f"{len(model._constraints)} constraints")
    print(f"Created in {gen_time} seconds\n")

    if ENABLE_DE:
        with RecursionLimiter(1_000):
            print("\nDE Solution:")
            de = DifferentialEvolutionOptimizer(
                model,
                max_iterations=DE_ITERATIONS,
                num_individuals=DE_POPULATION,
            )
            de.optimize()
            print("With costs:")
            pprint(de.solution.objective_values)
            print(f"In {de.solve_time} seconds\n")

        ## DE METRICS
        if PLOT:
            evolution_data = de.evolution_data
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
        with RecursionLimiter(1_000):
            print("\nPSO Solution:")
            pso = ParticleSwarmOptimizer(
                model,
                max_iterations=PSO_ITERATIONS,
                num_particles=PSO_SWARM,
            )
            print("With costs:")
            pso.optimize()
            pprint(pso.solution.objective_values)
            print(f"In {pso.solve_time} seconds\n")

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
