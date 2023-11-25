import pandas as pd
import plotly.express as px

from typing import NamedTuple


def read_data(path):
    return (
        pd.read_csv(path, header=None)
        .dropna(how="all", axis=0)
        .dropna(how="all", axis=1)
    )


class Machine(NamedTuple):
    id: int
    t0: int
    cluster: int
    fault_cost: int


class MaintenancePlan(NamedTuple):
    id: int
    k: int
    plan_cost: int


class Cluster(NamedTuple):
    id: int
    n: int
    b: int


class Solution(NamedTuple):
    x: list
    maintenance_cost: float
    fault_cost: float


def export_solution_pool(solution_pool, path):
    file = path + 'solutions.csv'
    solutions = list(map(lambda s: s.x, solution_pool))
    solutions = pd.DataFrame(solutions)
    solutions.drop_duplicates(inplace=True, keep="first")
    solutions.to_csv(file, index=False, header=False)

    print(f"Exported {len(solutions)} solutions to {path}")

def plot_objective_funtions(results: pd.DataFrame, path: str):
    fig = px.scatter(results, x='Maintenance Cost', y='Fault Cost', color='Total Cost')
    fig.write_html(path + 'objective_functions.html')

def plot_boxplot(results: pd.DataFrame, path: str, column: str):
    fig = px.box(results, x=column)
    fig.write_html(path + f'{column}_boxplot.html')

def plot_graphs(results: pd.DataFrame, path: str):
    plot_objective_funtions(results, path)
    plot_boxplot(results, path, 'Maintenance Cost')
    plot_boxplot(results, path, 'Fault Cost')