from argparse import ArgumentParser

from src import *


def parse_arguments():
    parser = ArgumentParser(description="Solves a CVRP instance")
    parser.add_argument(
        "-i",
        "--instance",
        type=str,
        help="Path to the instance file",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output file",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot the graph of the solution",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print the solution to the console",
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Create a random instance",
    )
    parser.add_argument(
        "-n",
        "--num_deliveries",
        type=int,
        help="Number of deliveries in the random instance",
        default=10,
    )
    parser.add_argument(
        "-m",
        "--num_vehicles",
        type=int,
        help="Number of vehicles in the random instance",
        default=3,
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        help="Seed for the random instance",
        default=42,
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.random:
        instance = create_random_instance(
            args.num_vehicles, args.num_deliveries, args.instance, args.seed
        )
    elif args.instance:
        instance = create_instance_from_data(args.instance)
    else:
        raise ValueError("No instance provided to the program: use -i or -r")

    problem = CVRPProblem(instance)
    problem.create_model()
    problem.export_model(args.output)
    problem.solve()
    solution = problem.create_solution()

    output = Output(instance, solution)
    output.write(args.output)

    if args.verbose:
        print(solution)

    if args.plot:
        output.plot_graph(args.output)


if __name__ == "__main__":
    main()
