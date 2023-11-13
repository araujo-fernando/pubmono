from __future__ import annotations
import os

import random as rd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import math
import json

from time import time
from pprint import pprint

from solver import Model, ParticleSwarmOptimizer, DifferentialEvolutionOptimizer


def dump_json_results(
    optimizer: ParticleSwarmOptimizer | DifferentialEvolutionOptimizer,
):
    solve_time = optimizer.solve_time
    solution = optimizer.solution
    evo_data = optimizer.evolution_data
    num_vars = solution.num_vars
    num_constrs = len(solution._constraints)
    objectives = solution.objective_values
    solution_variables_values = solution.export_solution

    if isinstance(optimizer, ParticleSwarmOptimizer):
        extension = "_pso.json"
        max_iterations = optimizer.max_iterations
        population = optimizer.num_particles
    else:
        extension = "_de.json"
        max_iterations = optimizer.max_iterations
        population = optimizer.num_individuals

    file_name = f"{max_iterations}it_{population}_ind{num_vars}var_{num_constrs}cnstr"

    experiment_data = {
        "solve_time": solve_time,
        "evo_data": evo_data,
        "num_vars": num_vars,
        "num_constrs": num_constrs,
        "objectives": objectives,
        "solution_variables_values": solution_variables_values,
        "population": population,
        "max_iterations": max_iterations,
    }
    to_dump = json.dumps(experiment_data)

    for i in range(10):
        name = file_name + f"_{i}"
        if not os.path.isfile("results/" + name + extension):
            file_name = name
            break

    with open("results/" + file_name + extension, "w") as f:
        f.write(to_dump)


def assemble_model(TOTAL_NOS=10, T=60) -> tuple[Model, float]:
    TOTAL_MERCADORIAS = TOTAL_NOS // 2
    model = Model()

    ## GERAÇÃO DOS DADOS BASE
    start_time = time()
    mercadorias = [f"mercadoria_{x}" for x in range(TOTAL_MERCADORIAS)]
    nos = [f"no_{x}" for x in range(TOTAL_NOS)]
    nos_clientes = rd.sample(nos, TOTAL_NOS // 5)
    nos_fornecedores = list(
        rd.sample(list(set(nos) - set(nos_clientes)), TOTAL_NOS // 5)
    )
    nos_intermediarios = list(set(nos) - set(nos_clientes) - set(nos_fornecedores))
    todos_pares = [
        (i, j) for i in nos for j in nos if (i != j) and (i not in nos_clientes)
    ]
    todos_pares_mercadorias = [(i, j, m) for i, j in todos_pares for m in mercadorias]
    fornecedores_mercadorias = [(i, m) for i in nos_fornecedores for m in mercadorias]
    ## GERAÇÃO DAS VARIÁVEIS
    p_0_m = model.create_real_variables("p_0_", mercadorias, lb=10, ub=500)
    p_1_m = model.create_real_variables("p_1_", mercadorias, lb=500, ub=1000)
    p_2_m = model.create_real_variables("p_2_", mercadorias, lb=250, ub=750)

    s_0_i_m = model.create_integer_variables(
        "s_0_", nos_intermediarios, lb=3000, ub=4000
    )
    s_1_i_m = model.create_integer_variables(
        "s_1_", nos_intermediarios, lb=2000, ub=3000
    )
    s_2_i_m = model.create_integer_variables(
        "s_2_", nos_intermediarios, lb=1000, ub=2000
    )

    b_i = model.create_binary_variables("b_", nos)

    c_i_j_m = model.create_real_variables("c_", todos_pares_mercadorias, lb=0, ub=100)
    f_i_j_m = model.create_real_variables("f_", todos_pares_mercadorias, lb=0, ub=100)
    g_j_m = model.create_integer_variables(
        "g_", fornecedores_mercadorias, lb=50, ub=150
    )
    w = model.create_real_variable("w", lb=0, ub=T)

    ## GERAÇÃO DAS CONSTANTES
    d_j_m = {(i, m): rd.uniform(10, 100) for i in nos_clientes for m in mercadorias}
    h_i_m = {(i, m): rd.uniform(100, 200) for i in nos for m in mercadorias}
    e_i = {i: rd.uniform(1000, 10000) for i in nos if i not in nos_clientes}
    h_m = {m: rd.uniform(0, 20) for m in mercadorias}
    v_i = {i: rd.uniform(50, 500) for i in nos}
    u_i = {i: rd.uniform(5, 50) for i in nos}

    alpha_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    eps_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    gama_m = {m: rd.uniform(0.001, 2) for m in mercadorias}
    beta_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    r_m = {m: alpha_m[m] * beta_m[m] / gama_m[m] for m in mercadorias}

    ## GERAÇÃO DA FUNÇÃO OBJETIVO
    objetivo = (
        sum(
            sum(
                (
                    (p_1_m[m] - p_0_m[m]) * s_0_i_m.get((i, m), 0)
                    - (p_1_m[m] - p_2_m[m]) * s_1_i_m.get((i, m), 0)
                    - (p_2_m[m] + h_m[m]) * s_2_i_m.get((i, m), 0)
                )
                for m in mercadorias
            )
            for i in nos_clientes
        )
        - sum(
            sum(
                (c_i_j_m[(i, j, m)] + v_i[i]) * f_i_j_m[(i, j, m)]
                for i, j in todos_pares
            )
            for m in mercadorias
        )
        - sum(u_i[i] * b_i[i] for i in nos)
    )

    model.set_objective(objetivo)
    ## GERAÇÃO DAS RESTRIÇÕES DE IGUALDADE
    r_18 = [
        g_j_m.get((j, m), 0)
        + s_0_i_m.get((j, m), 0)
        + sum(f_i_j_m[(i, j, m)] for i in nos if (i, j) in todos_pares)
        - d_j_m.get((j, m), 0)
        + s_2_i_m.get((j, m), 0)
        - sum(f_i_j_m[(j, k, m)] for k in nos if (j, k) in todos_pares)
        for j in nos
        for m in mercadorias
    ]
    model.insert_eq_zero_constraints(r_18)

    ## GERAÇÃO DAS RESTRIÇÕES DE MENOR IGUAL
    r_19 = [
        sum(f_i_j_m[(i, j, m)] for j in nos if (i, j) in todos_pares) - e_i.get(i, 0)
        for i in nos
        for m in mercadorias
    ]
    r_20 = [
        g_j_m.get((i, m), 0) - h_i_m.get((i, m), 0) for i in nos for m in mercadorias
    ]
    r_21 = [
        d_j_m.get((j, m), 0)
        - sum(f_i_j_m[(i, j, m)] for i in nos if (i, j) in todos_pares)
        for j in nos_clientes
        for m in mercadorias
    ]
    r_22 = [
        (
            s_0_i_m.get((i, m), 0) ** beta_m[m]
            - r_m[m] * (w ** gama_m[m]) / (p_1_m[m] ** eps_m[m])
        )
        ** (1 / beta_m[m])
        - s_1_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_23 = [
        (
            s_0_i_m.get((i, m), 0) ** beta_m[m]
            - r_m[m] * (w ** gama_m[m]) / (p_1_m[m] ** eps_m[m])
            - r_m[m] * (T ** gama_m[m] - w ** gama_m[m]) / (p_2_m[m] ** eps_m[m])
        )
        ** (1 / beta_m[m])
        - s_2_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_24_1 = [p_0_m[m] - p_2_m[m] for m in mercadorias]
    r_24_2 = [p_2_m[m] - p_1_m[m] for m in mercadorias]
    r_26_1 = [
        s_2_i_m.get((i, m), 0) - s_1_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_26_2 = [
        s_1_i_m.get((i, m), 0) - s_0_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]

    model.insert_lt_zero_constraints(r_19)
    model.insert_lt_zero_constraints(r_20)
    model.insert_lt_zero_constraints(r_21)
    model.insert_lt_zero_constraints(r_22)
    model.insert_lt_zero_constraints(r_23)
    model.insert_lt_zero_constraints(r_24_1)
    model.insert_lt_zero_constraints(r_24_2)
    model.insert_lt_zero_constraints(r_26_1)
    model.insert_lt_zero_constraints(r_26_2)
    end_time = time()

    return model, (end_time - start_time)


def assemble_model_from_data(path: str, source_level_name: str, sink_level_name: str, T=60) -> tuple[Model, float]:
    model = Model()

    ## CARREGAMENTO DOS DADOS BASE
    start_time = time()

    tabela_baseline = pd.read_csv(f"{path}/baseline.csv")
    tabela_custo_nos = pd.read_csv(f"{path}/custo_nos.csv")
    tabela_demanda = pd.read_csv(f"{path}/demanda.csv")
    tabela_frete = pd.read_csv(f"{path}/frete.csv")
    tabela_nos = pd.read_csv(f"{path}/nos_anonim.csv")
    tabela_preco = pd.read_csv(f"{path}/valor_mercadoria.csv")
    tabela_skus = pd.read_csv(f"{path}/skus_anonim.csv")

    mercadorias = tabela_skus["ids"].tolist()
    nos = tabela_nos["idn"].tolist()
    nos_clientes = tabela_nos[tabela_nos["nivel"] == sink_level_name]["idn"].tolist()
    nos_fornecedores = tabela_nos[tabela_nos["nivel"] == source_level_name]["idn"].tolist()
    nos_intermediarios = list(set(nos) - set(nos_clientes) - set(nos_fornecedores))

    todos_pares = tabela_frete[["origem", "destino"]].drop_duplicates().values.tolist()  
    todos_pares_mercadorias = tabela_frete[["origem", "destino", "sku"]].drop_duplicates().values.tolist()
    todos_pares_mercadorias = list(map(tuple, todos_pares_mercadorias))

    fornecedores_mercadorias = tabela_frete[tabela_frete["origem"].isin(nos_fornecedores)][["origem", "sku"]].drop_duplicates().values.tolist()  
    fornecedores_mercadorias = list(map(tuple, fornecedores_mercadorias))

    ## GERAÇÃO DAS VARIÁVEIS
    preco_max = 10**(math.log10(tabela_preco["valorMercadoria"].max())//1+1)
    p_0_m = model.create_real_variables("p_0_", mercadorias, lb=0, ub=preco_max)
    p_1_m = model.create_real_variables("p_1_", mercadorias, lb=0, ub=preco_max)
    p_2_m = model.create_real_variables("p_2_", mercadorias, lb=0, ub=preco_max)

    demanda_total = 10**(math.log10(tabela_demanda["demanda"].sum())//1+1)
    s_0_i_m = model.create_integer_variables("s_0_", nos_intermediarios, lb=0, ub=demanda_total)
    s_1_i_m = model.create_integer_variables("s_1_", nos_intermediarios, lb=0, ub=demanda_total)
    s_2_i_m = model.create_integer_variables("s_2_", nos_intermediarios, lb=0, ub=demanda_total)

    b_i = model.create_binary_variables("b_", nos)

    frete_max = 10**(math.log10(tabela_frete["custo"].max())//1+1)
    c_i_j_m = model.create_real_variables("c_", todos_pares_mercadorias, lb=0, ub=frete_max)
    f_i_j_m = model.create_real_variables("f_", todos_pares_mercadorias, lb=0, ub=demanda_total)
    g_j_m = model.create_integer_variables("g_", fornecedores_mercadorias, lb=0, ub=demanda_total)
    w = model.create_real_variable("w", lb=0, ub=T)

    ## GERAÇÃO DAS CONSTANTES
    d_j_m = pd.DataFrame(tabela_demanda.groupby(["no", "sku"])["demanda"].sum()).to_dict()
    h_i_m = {(i, m): h for i, h in tabela_custo_nos[["no", "capFornecimento"]].values for m in mercadorias}
    e_i = tabela_custo_nos.set_index("no")["capExpedicao"].to_dict()
    h_m = pd.DataFrame(0.1*tabela_preco.groupby("sku")["valorMercadoria"].mean()).to_dict()
    v_i = tabela_custo_nos.set_index("no")["custoVariavelExpedicao"].to_dict()
    u_i = tabela_custo_nos.set_index("no")["custoFixo"].to_dict()

    alpha_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    eps_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    gama_m = {m: rd.uniform(0.001, 2) for m in mercadorias}
    beta_m = {m: rd.uniform(0.001, 0.999) for m in mercadorias}
    r_m = {m: alpha_m[m] * beta_m[m] / gama_m[m] for m in mercadorias}

    ## GERAÇÃO DA FUNÇÃO OBJETIVO
    objetivo = (
        sum(
            sum(
                (
                    (p_1_m.get(m, 0) - p_0_m.get(m, 0)) * s_0_i_m.get((i, m), 0)
                    - (p_1_m.get(m, 0) - p_2_m.get(m, 0)) * s_1_i_m.get((i, m), 0)
                    - (p_2_m.get(m, 0) + h_m.get(m, 0)) * s_2_i_m.get((i, m), 0)
                )
                for m in mercadorias
            )
            for i in nos_clientes
        )
        - sum(
            sum(
                (c_i_j_m[(i, j, m)] + v_i[i]) * f_i_j_m[(i, j, m)]
                for i, j in todos_pares
            )
            for m in mercadorias
        )
        - sum(u_i.get(i, 0) * b_i[i] for i in nos)
    )

    model.set_objective(objetivo)
    ## GERAÇÃO DAS RESTRIÇÕES DE IGUALDADE
    r_18 = [
        g_j_m.get((j, m), 0)
        + s_0_i_m.get((j, m), 0)
        + sum(f_i_j_m[(i, j, m)] for i in nos if (i, j) in todos_pares)
        - d_j_m.get((j, m), 0)
        + s_2_i_m.get((j, m), 0)
        - sum(f_i_j_m[(j, k, m)] for k in nos if (j, k) in todos_pares)
        for j in nos
        for m in mercadorias
    ]
    model.insert_eq_zero_constraints(r_18)

    ## GERAÇÃO DAS RESTRIÇÕES DE MENOR IGUAL
    r_19 = [
        sum(f_i_j_m[(i, j, m)] for j in nos if (i, j) in todos_pares) - e_i.get(i, 0)
        for i in nos
        for m in mercadorias
    ]
    r_20 = [
        g_j_m.get((i, m), 0) - h_i_m.get((i, m), 0) for i in nos for m in mercadorias
    ]
    r_21 = [
        d_j_m.get((j, m), 0)
        - sum(f_i_j_m[(i, j, m)] for i in nos if (i, j) in todos_pares)
        for j in nos_clientes
        for m in mercadorias
    ]
    r_22 = [
        (
            s_0_i_m.get((i, m), 0) ** beta_m[m]
            - r_m[m] * (w ** gama_m[m]) / (p_1_m[m] ** eps_m[m])
        )
        ** (1 / beta_m[m])
        - s_1_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_23 = [
        (
            s_0_i_m.get((i, m), 0) ** beta_m[m]
            - r_m[m] * (w ** gama_m[m]) / (p_1_m[m] ** eps_m[m])
            - r_m[m] * (T ** gama_m[m] - w ** gama_m[m]) / (p_2_m[m] ** eps_m[m])
        )
        ** (1 / beta_m[m])
        - s_2_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_24_1 = [p_0_m[m] - p_2_m[m] for m in mercadorias]
    r_24_2 = [p_2_m[m] - p_1_m[m] for m in mercadorias]
    r_26_1 = [
        s_2_i_m.get((i, m), 0) - s_1_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]
    r_26_2 = [
        s_1_i_m.get((i, m), 0) - s_0_i_m.get((i, m), 0)
        for i in nos
        for m in mercadorias
    ]

    model.insert_lt_zero_constraints(r_19)
    model.insert_lt_zero_constraints(r_20)
    model.insert_lt_zero_constraints(r_21)
    model.insert_lt_zero_constraints(r_22)
    model.insert_lt_zero_constraints(r_23)
    model.insert_lt_zero_constraints(r_24_1)
    model.insert_lt_zero_constraints(r_24_2)
    model.insert_lt_zero_constraints(r_26_1)
    model.insert_lt_zero_constraints(r_26_2)
    end_time = time()

    return model, (end_time - start_time)



def bark(model):
    # placeholder method to store optimization flux
    de = DifferentialEvolutionOptimizer(model, max_iterations=100, num_individuals=500)
    pso = ParticleSwarmOptimizer(model, max_iterations=300, num_particles=500)
    best_individual = de.optimize()
    print("DE Solution:")
    pprint({name: var._value for name, var in best_individual._vars.items()})
    print("With costs:")
    pprint(best_individual.objective_values)
    print(f"In {de.solve_time} seconds\n")

    best_particle = pso.optimize()
    print("PSO Solution:")
    pprint({name: var._value for name, var in best_particle._vars.items()})
    print("With costs:")
    pprint(best_particle.objective_values)
    print(f"In {pso.solve_time} seconds\n")

    ## DE METRICS
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
