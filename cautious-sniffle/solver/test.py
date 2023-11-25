from concurrent.futures import ProcessPoolExecutor

from model import Model
from pso import ParticleSwarmOptimizer
from de import DifferentialEvolutionOptimizer
from experiments import assemble_model, dump_json_results


def create_pso(model, num_particles, max_iterations):
    ps = ParticleSwarmOptimizer(
        model, num_particles=num_particles, max_iterations=max_iterations
    )
    return ps


def create_de(model, num_particles, max_iterations):
    de = DifferentialEvolutionOptimizer(
        model, num_individuals=num_particles, max_iterations=max_iterations
    )
    return de


def realize_experiments(
    model: Model,
    PSO_SWARM=500,
    DE_POPULATION=250,
    PSO_ITERATIONS=900,
):
    DE_ITERATIONS = PSO_ITERATIONS // 3

    with ProcessPoolExecutor(10) as exec:
        results = list(
            exec.map(
                create_pso,
                [model.copy() for _ in range(10)],
                [PSO_SWARM for _ in range(10)],
                [PSO_ITERATIONS for _ in range(10)],
            )
        )
    len(results)
    for result in results:
        dump_json_results(result)

    with ProcessPoolExecutor(10) as exec:
        results = list(
            exec.map(
                create_de,
                [model.copy() for _ in range(10)],
                [DE_POPULATION for _ in range(10)],
                [DE_ITERATIONS for _ in range(10)],
            )
        )
    len(results)
    for result in results:
        dump_json_results(result)


if __name__ == "__main__":
    total_nos = [8, 9]
    population = [50, 100, 150, 250, 300, 350, 400, 450, 500]
    iterations = [1000]
    for nos in total_nos:
        model, t = assemble_model(nos)
        print(f"Model time: {t} for {nos} nodes with {model.num_vars} variables.")
        for pop in population:
            for iter in iterations:
                print(nos, pop, iter)
                realize_experiments(model, pop, pop//2, iter)


