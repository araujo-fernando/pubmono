from argparse import ArgumentParser
from tqdm import tqdm
from pandas import DataFrame

from os import mkdir
from os.path import isdir, dirname

from src import *


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "--horizon",
        type=int,
        default=5,
        help="Horizon of the problem, defaults to 5 years",
    )
    parser.add_argument(
        "--path", type=str, default="data/", help="Path to the data files"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        default=False,
        help="Runs until first feasible sol",
    )
    parser.add_argument(
        "-hv",
        "--hipervolume",
        action="store_true",
        default=False,
        help="Runs maximization of hipervolume equivalent problem",
    )
    parser.add_argument("--verbose", action="store_true", default=False)

    args = parser.parse_args()

    if args.path[-1] != "/":
        args.path = args.path + "/"

    if not isdir(args.path):  # type: ignore
        raise ValueError(f"Invalid path: {args.path}")

    if args.once and args.hipervolume:
        raise ValueError("Invalid arguments: --once and --hipervolume cannot be used together")

    return args


def create_output_path(path):
    parent = dirname(path)

    output_path = parent + "/output/"
    if not isdir(output_path):
        mkdir(output_path)

    return output_path


def solve_problem_and_create_solution_pool_with_eps(args, problem: ProblemInstance):
    solution_pool = list()
    max_maintenance_cost = problem.get_max_maintenance_cost()
    min_maintenance_cost = problem.get_min_maintenance_cost()
    step = problem.get_maintenance_cost_step()
    solution_pool = list()
    mode = Modes.MIN_FAULT_COST
    with tqdm(total=max_maintenance_cost, desc="Optimizing") as pbar:
        for eps in range(min_maintenance_cost, max_maintenance_cost + step, step):
            pbar.set_postfix_str(f"eps: {eps:6d}")
            model = Model(problem, eps, mode, args.verbose)
            model.optimize()

            solution = model.export_solution()

            if solution:
                solution_pool.append(solution)
                if args.once:
                    break

            if args.verbose:
                if solution:
                    print(
                        f"Solution found with costs: {solution.maintenance_cost:9d}, {solution.fault_cost:9d}"
                    )
                else:
                    print(f"No solution found with eps: {eps}")

            pbar.update(step)

    return solution_pool


def solve_problem_and_create_solution_pool_with_hipervolume(
    args, problem: ProblemInstance
):
    solution_pool = list()

    model = ModelHiperV(problem, args.verbose)
    model.optimize()
    solution_pool = model.export_solution_pool()

    if args.verbose:
        for sol in solution_pool:
            print(
                f"Solution found with costs: {sol.maintenance_cost:9d}, {sol.fault_cost:9d}"
            )

    if not solution_pool:
        print(f"No solution found")
        quit()

    return solution_pool


def main(args):
    path = args.path
    verbose = args.verbose

    output_path = create_output_path(path)

    problem = ProblemInstance(path, args.horizon)

    if verbose:
        problem.print_data()

    if args.hipervolume:
        solution_pool = solve_problem_and_create_solution_pool_with_hipervolume(
            args, problem
        )
    else:
        solution_pool = solve_problem_and_create_solution_pool_with_eps(args, problem)

    export_solution_pool(solution_pool, output_path)
    costs = set(map(lambda s: (s.maintenance_cost, s.fault_cost), solution_pool))
    costs = DataFrame(costs, columns=["Maintenance Cost", "Fault Cost"])
    costs.sort_values(by=["Maintenance Cost", "Fault Cost"], inplace=True)
    costs["Total Cost"] = costs["Maintenance Cost"] + costs["Fault Cost"]
    if verbose:
        print(costs)

    plot_graphs(costs, output_path)


if __name__ == "__main__":
    args = parse_args()
    main(args)
