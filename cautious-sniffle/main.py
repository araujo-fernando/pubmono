import numpy as np
import seaborn as sns

from pprint import pprint

from solver import *

PLOT = True
INSTANCE = "elfa"
NUM_SKUS = 1
filtro_skus = ["NUTRICAO", "MATERIAIS", "GENERICO", "ESPECIALIDADES", "SIMILAR"]
## CONFIGURAÇÕES PARA SOLVERS
ENABLE_PSO = True
ENABLE_DE = False

PSO_SWARM = 300
DE_POPULATION = 100

PSO_ITERATIONS = 10_000
DE_ITERATIONS = 10_000
## CONFIGURAÇÕES PARA MONTAGEM DO PROBLEMA
T = 360
DATA_PATH = f"data/{INSTANCE}"

if __name__ == "__main__":
    if DATA_PATH:
        model, gen_time = assemble_model_from_data(
            DATA_PATH, "Fornecedor", "Cliente", T, filtro_skus[0:NUM_SKUS]
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
            print("\nWith costs:")
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
            fig = objs_evo.get_figure()
            if fig is not None:
                fig.savefig(f"de_model_{INSTANCE}_{NUM_SKUS}_{T}_objs.png")

            pen_evo = sns.heatmap(penalties)
            fig = objs_evo.get_figure()
            if fig is not None:
                fig.savefig(f"de_model_{INSTANCE}_{NUM_SKUS}_{T}_pen.png")

    if ENABLE_PSO:
        with RecursionLimiter(1_000):
            print("\nPSO Solution:")
            pso = ParticleSwarmOptimizer(
                model,
                max_iterations=PSO_ITERATIONS,
                num_particles=PSO_SWARM,
            )
            print("\nWith costs:")
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
            fig = objs_evo.get_figure()
            if fig is not None:
                fig.savefig(f"pso_model_{INSTANCE}_{NUM_SKUS}_{T}_objs.png")

            pen_evo = sns.heatmap(penalties)
            fig = objs_evo.get_figure()
            if fig is not None:
                fig.savefig(f"pso_model_{INSTANCE}_{NUM_SKUS}_{T}_pen.png")
