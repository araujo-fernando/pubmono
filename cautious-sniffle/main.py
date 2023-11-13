import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pprint import pprint

from solver import *

PLOT = False
PATH = "dados/elfa"
## CONFIGURAÇÕES PARA SOLVERS
PSO_SWARM = 50
DE_POPULATION = 25

PSO_ITERATIONS = 9
DE_ITERATIONS = PSO_ITERATIONS//3
## CONFIGURAÇÕES PARA MONTAGEM DO PROBLEMA
T = 60

model, gen_time = assemble_model_from_data(PATH, "Fornecedor", "Cliente", T)

print("Model Statistics:")
print(f"{len(model._vars)} variables")
print(f"{len(model._constraints)} constraints\n")
print(f"Created in {gen_time} seconds\n")

print("DE Solution:")
de = DifferentialEvolutionOptimizer(
    model, max_iterations=DE_ITERATIONS, num_individuals=DE_POPULATION
)
print("With costs:")
pprint(de.solution.objective_values)
print(f"In {de.solve_time} seconds\n")

print("PSO Solution:")
pso = ParticleSwarmOptimizer(
    model, max_iterations=PSO_ITERATIONS, num_particles=PSO_SWARM
)
print("With costs:")
pprint(pso.solution.objective_values)
print(f"In {pso.solve_time} seconds\n")


## DE METRICS
if not PLOT:
    quit()
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

## PSO METRICS
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
