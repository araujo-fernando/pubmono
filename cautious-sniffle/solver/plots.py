from __future__ import annotations

import matplotlib
import seaborn as sns
import numpy as np

import json
import os
import re

from pprint import pprint
from tqdm import tqdm
from matplotlib import pyplot as plt

def normalize_evolution_data(evolution_data: list[list[list[float]]]):
    objective_pen = [[sum(val) for val in it] for it in evolution_data]
    objectives = [[val[0] for val in it] for it in evolution_data]
    penalties = [[val[1] for val in it] for it in evolution_data]

    for data in objective_pen:
        data.sort()
    for data in objectives:
        data.sort()
    for data in penalties:
        data.sort()

    objective_pen = list(map(list, zip(*objective_pen)))
    objectives = list(map(list, zip(*objectives)))
    penalties = list(map(list, zip(*penalties)))

    objective_pen = np.array(objective_pen)
    min_value = objective_pen.min()
    max_value = objective_pen.max()
    objective_pen = (objective_pen - min_value) / (max_value - min_value)

    objectives = np.array(objectives)
    min_value = objectives.min()
    max_value = objectives.max()
    objectives = (objectives - min_value) / (max_value - min_value)

    penalties = np.array(penalties)
    min_value = penalties.min()
    max_value = penalties.max()
    penalties = (penalties - min_value) / (max_value - min_value)

    return objective_pen, objectives, penalties


def create_heatmaps(parameters: list, algo: str):
    if len(parameters) == 0:
        return

    def get_best_execution_data(params: tuple, algo: str="de"):
        iters, indiv, vars, constrs = params
        experiment_files = [
            path + f"{iters}it_{indiv}_ind{vars}var_{constrs}cnstr_{i}_{algo}.json"
            for i in range(10)
        ]

        evo_data = [[[]]]
        objectives = None
        for experiment in experiment_files:
            dados = load_file_data(experiment)
            obj = dados["objectives"]
            if objectives is None:
                objectives = obj
                evo_data = dados["evo_data"]
            if sum(obj) > sum(objectives):
                objectives = obj
                evo_data = dados["evo_data"]

        return evo_data

    cenarios = {(87, 86): "A", (181, 153): "B", (251, 177): "C", (435, 268): "D", (559, 300): "E", (774, 420): "F"}

    fig, axn = plt.subplots(3, 2, sharex=True, sharey=True, figsize=(9, 9))
    
    for i in range(len(parameters)):
        par = parameters[i]
        iter, pop, vars, constrs = par
        cenario = cenarios[(vars, constrs)]

        xlabels = ['{0:d}'.format(i) for i in range(1, iter+1, iter//10)]
        xticks = [i for i in range(1, iter+1, iter//10)]
        ylabels = ['{0:d}'.format(i) for i in range(1, pop+1, pop//10)]
        yticks = [i for i in range(1, pop+1, pop//10)]

        evo_data = get_best_execution_data(par, algo)
        pen_obj, objs, pens = normalize_evolution_data(evo_data)
        ax = plt.subplot(3, 2, i+1)
        sns.heatmap(objs, annot=False, ax=ax)
        ax.set_title(f"Função Objetivo do Cenário {cenario}")
        plt.xticks(xticks, xlabels)
        plt.yticks(yticks, ylabels)
        plt.xlim(None, None)
        if algo=="de":
            ax.set_xscale("log")
            ax.set_xticks([1, 10, 100, 200, 300])
            ax.get_xaxis().set_major_formatter(matplotlib.ticker.LogFormatter())

    plt.setp(axn[-1, :], xlabel='Iteração')
    plt.setp(axn[:, 0], ylabel='Indivíduo')
    plt.savefig(f"figures/heat/{algo}_{pop}", dpi=200)
    plt.close()

def load_file_data(file_name: str):
    with open(file_name, "r") as f:
        data = json.loads(f.read())

    return data


def create_resume_table(pso_params: list, de_params: list):
    def extract_data(params: tuple, algo: str="de"):
        iters, indiv, vars, constrs = params
        experiment_files = [
            path + f"{iters}it_{indiv}_ind{vars}var_{constrs}cnstr_{i}_{algo}.json"
            for i in range(10)
        ]

        solve_times = list()
        objectives = list()
        penalties = list()
        for experiment in experiment_files:
            dados = load_file_data(experiment)
            solve_times.append(dados["solve_time"]/60)
            objectives.append(dados["objectives"][0]/1000)
            penalties.append(dados["objectives"][1]/1000)

        return indiv, np.mean(solve_times), np.std(solve_times), np.min(objectives), np.max(objectives), np.mean(objectives), np.std(objectives)

    cenarios ={(87, 86): "A", (181, 153): "B", (251, 177): "C", (435, 268): "D", (559, 300): "E", (774, 420): "F"}

    ps_data = ""
    de_data = ""
    comp_data = ""
    for i in range(len(pso_params)):
        pso_param = pso_params[i]
        de_param = de_params[i]
        vars = pso_param[2]
        constrs = pso_param[3]

        ps_pop, ps_time, ps_time_std, ps_min, ps_max, ps_mean, ps_std = extract_data(pso_param, "pso")
        de_pop, de_time, de_time_std, de_min, de_max, de_mean, de_std = extract_data(de_param, "de")
        time_ratio = 100*ps_time/de_time

        ps_data += f"${ps_pop}$&${ps_time:.2f}\\pm{ps_time_std:.2f}$&${ps_min:.2f}$&${ps_max:.2f}$&${ps_mean:.2f}\\pm{ps_std:.2f}$\\\\\n"
    
        de_data += f"${de_pop}$&${de_time:.2f}\\pm{de_time_std:.2f}$&${de_min:.2f}$&${de_max:.2f}$&${de_mean:.2f}\\pm{de_std:.2f}$\\\\\n"

        comp_data += f"${de_pop}$&${ps_pop}$&${time_ratio:.2f}\\%$\\\\\n"

    def header(algo):
        return (
            "\\begin{table}[h]\n"
            + "\\centering\n"
            + "\\caption{Resultados dos experimentos para os modelos do cenário "
            + f"{cenarios[(vars, constrs)]} otimizados com {algo}"
            + "\\label{"
            + f"tab:resultado_cenario_{cenarios[(vars, constrs)]}_{algo}"
            + "}}\\vspace{0.5cm}\n"
            + "\\begin{tabular}{rrrrr}\n"
            + "\\hline\n"
            + "\\textbf{População}&\\textbf{Tempo Médio}&\\textbf{Pior Objetivo}&\\textbf{Melhor Objetivo}&\\textbf{Média dos Objetivos}\\\\\n"
            + "\\hline\n"
        )

    def header_2():
        return (
            "\\begin{table}[h]\n"
            + "\\centering\n"
            + "\\caption{Tempo relativo entre a otimização via PSO e NDE"
            + f" para o cenário {cenarios[(vars, constrs)]}"
            + "\\label{"
            + f"tab:comparacao_cenario_{cenarios[(vars, constrs)]}"
            + "}}\n\\vspace{0.5cm}\n"
            + "\\begin{tabular}{rrr}\n"
            + "\\hline\n"
            + "\\textbf{População NDE}&\\textbf{População PSO}&\\textbf{Tempo Relativo}\\\\\n"
            + "\\hline\n"
        )

    def tail():
        return(
            "\\end{tabular}\n"
            + "\\end{table}"
        )

    with open(f"analisys/{cenarios[(vars, constrs)]}_ps_table.tex", "w") as f:
        f.write(header("PSO"))
        f.write(ps_data)
        f.write(tail())
    with open(f"analisys/{cenarios[(vars, constrs)]}_de_table.tex", "w") as f:
        f.write(header("NDE"))
        f.write(de_data)
        f.write(tail())
    with open(f"analisys/{cenarios[(vars, constrs)]}_comp_table.tex", "w") as f:
        f.write(header_2())
        f.write(comp_data)
        f.write(tail())


def create_paretos(parameters: list, algo: str):
    def get_best_execution_data(params: tuple, algo: str="de"):
        iters, indiv, vars, constrs = params
        experiment_files = [
            path + f"{iters}it_{indiv}_ind{vars}var_{constrs}cnstr_{i}_{algo}.json"
            for i in range(10)
        ]

        evo_data = [[[]]]
        objectives = None
        for experiment in experiment_files:
            dados = load_file_data(experiment)
            obj = dados["objectives"]
            if objectives is None:
                objectives = obj
                evo_data = dados["evo_data"]
            if sum(obj) > sum(objectives):
                objectives = obj
                evo_data = dados["evo_data"]

        return evo_data

    def pareto_frontier(data, maxX = True, maxY = True):
        myList = sorted(data, reverse=maxX)
        p_front = [myList[0]]    
        for pair in myList[1:]:
            if maxY: 
                if pair[1] >= p_front[-1][1]:
                    p_front.append(pair)
            else:
                if pair[1] <= p_front[-1][1]: 
                    p_front.append(pair) 
        p_frontX = [pair[0] for pair in p_front]
        p_frontY = [pair[1] for pair in p_front]
        return p_frontX, p_frontY

    cenarios = {(87, 86): "A", (181, 153): "B", (251, 177): "C", (435, 268): "D", (559, 300): "E", (774, 420): "F"}

    fig, axn = plt.subplots(3, 3, sharex=True, sharey=True, figsize=(10, 10))

    for i in range(len(parameters)):
        par = parameters[i]
        iter, pop, vars, constrs = par
        cenario = cenarios[(vars, constrs)]

        evo_data = get_best_execution_data(par, algo)
        data = [val for it in evo_data for val in it]
        pareto_x, pareto_y = pareto_frontier(data)
        # pen_obj, objs, pens = normalize_evolution_data(evo_data)
        ax = plt.subplot(3, 3, i+1)
        sns.scatterplot(x=np.array(pareto_x), y=np.array(pareto_y) )
        ax.set_title(f"{pop} indivíduos")
        plt.axes

    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))    
    plt.setp(axn[-1, :], xlabel='Função Objetivo')
    plt.setp(axn[:, 0], ylabel='Penalização')
    plt.savefig(f"figures/pareto/{cenario}_{algo}", dpi=200)
    plt.close()

# ['solve_time', 'evo_data', 'num_vars', 'num_constrs', 'objectives',
#  'solution_variables_values', 'population', 'max_iterations']

path = "results/"
files = os.listdir(path)
pso_files = [f for f in files if f.endswith("pso.json")]
de_files = [f for f in files if f.endswith("de.json")]

regex = r"(\d+)it_(\d+)_ind(\d+)var_(\d+)"

all_pso_params = list(set(re.match(regex, arq).groups() for arq in pso_files))
all_de_params = list(set(re.match(regex, arq).groups() for arq in de_files))

# iterations, population, variables, constraints
# variables = {"87", "181", "251", "435", "559", "774"}
# for vari in tqdm(variables):
#     pso_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_pso_params if p[0] == "1000" and p[2] == vari]
#     de_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_de_params if p[0] == "333" and p[2] == vari]

#     pso_params = sorted(pso_params, key=lambda p: (p[1], p[2], p[3]))
#     de_params = sorted(de_params, key=lambda p: (p[1], p[2], p[3]))

#     create_resume_table(pso_params, de_params)

# iterations, population, variables, constraints
# variables = {"87", "181", "251", "435", "559", "774"}
# for vari in tqdm(variables):
#     pso_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_pso_params if p[0] == "1000" and p[2] == vari and p[1] != "200"]
#     de_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_de_params if p[0] == "333" and p[2] == vari and p[1] != "100"]

#     pso_params = sorted(pso_params, key=lambda p: (p[1], p[2], p[3]))
#     de_params = sorted(de_params, key=lambda p: (p[1], p[2], p[3]))
#     create_paretos(de_params, "de")
#     create_paretos(pso_params, "pso")

# iterations, population, variables, constraints
population = [500 - 50*val for val in range(10)]
for pop in tqdm(population):
    pso_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_pso_params if p[0] == "1000" and int(p[1]) == pop and p[1] != "200"]
    de_params = [(int(p[0]), int(p[1]), int(p[2]), int(p[3])) for p in all_de_params if p[0] == "333" and int(p[1]) == pop//2 and p[1] != "100"]

    pso_params = sorted(pso_params, key=lambda p: (p[1], p[2], p[3]))
    de_params = sorted(de_params, key=lambda p: (p[1], p[2], p[3])) 

    create_heatmaps(de_params, "de")
    # create_heatmaps(pso_params, "pso")
