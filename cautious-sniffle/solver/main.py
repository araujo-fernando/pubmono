import imp
import numpy as np
import random as rd
import matplotlib.pyplot as plt
import seaborn as sns

from pprint import pprint
from time import time

from solver import *

from experiments import assemble_model
PLOT = False
## CONFIGURAÇÕES PARA SOLVERS
PSO_SWARM = 500
DE_POPULATION = 250

PSO_ITERATIONS = 900
DE_ITERATIONS = PSO_ITERATIONS//3
## CONFIGURAÇÕES PARA MONTAGEM DO PROBLEMA
T = 60
TOTAL_NOS = 10

model, gen_time = assemble_model(TOTAL_NOS, T)

print("Model Statistics:")
print(f"{len(model._vars)} variables")
print(f"{len(model._constraints)} constraints\n")
print(f"Created in {gen_time} seconds\n")

de = DifferentialEvolutionOptimizer(
    model, max_iterations=DE_ITERATIONS, num_individuals=DE_POPULATION
)
pso = ParticleSwarmOptimizer(
    model, max_iterations=PSO_ITERATIONS, num_particles=PSO_SWARM
)

print("PSO Solution:")
pso_solution = pso.optimize()
# pprint({name: var._value for name, var in pso_solution._vars.items()})
print("With costs:")
pprint(pso_solution.objective_values)
print(f"In {pso.solve_time} seconds\n")
 
print("DE Solution:")
de_solution = de.optimize()
# pprint({name: var._value for name, var in de_solution._vars.items()})
print("With costs:")
pprint(de_solution.objective_values)
print(f"In {de.solve_time} seconds\n")

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
