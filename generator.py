import random
import json
import itertools

chars = list('abcdefghijklmnopqrstuvwxyzäöü')
ITERATIONS = 100
POPULATION_SIZE = 100
SELECTED_COUNT = 33
MUTATION_COUNT = 33
MUTATION_RATE = 0.1


def main():
    population = generate_population(POPULATION_SIZE)

    with open('data.json') as file:
        frequency = json.load(file)['single']

    for i in range(1, ITERATIONS + 1):
        fitnesses = evaluate_population(population, frequency)
        print(f'Iteration: {i} Highest fitness: {max(fitnesses)}')
        selected = select_genotypes(population, fitnesses, SELECTED_COUNT)
        mutated = mutate(selected, MUTATION_RATE, MUTATION_COUNT)
        new_count = POPULATION_SIZE - MUTATION_COUNT - SELECTED_COUNT
        new_gen = generate_population(new_count)
        population = list(selected) + mutated + new_gen
    else:
        best = population[fitnesses.index(max(fitnesses))]
        print_layout(best)


def print_layout(genotype):
    print(genotype[:11])
    print(genotype[11:22])
    print(genotype[22:29])


def mutate_char(char, genotype, rate):
    if random.random() < rate/100:
        index1 = genotype.index(char)
        index2 = random.randint(0, len(genotype) - 1)
        genotype[index1], genotype[index2] = genotype[index2], genotype[index1]


def mutate(selected, rate, n):
    mutated = []
    source = itertools.cycle(selected)
    for i in range(n):
        genotype = next(source)[:]
        for i in range(len(genotype)):
            if random.random() < rate:
                index = random.randint(0, len(genotype) - 1)
                genotype[i], genotype[index] = genotype[index], genotype[i]
        mutated.append(genotype)
    return mutated


def evaluate_population(population, frequency):
    fitnesses = []
    for genotype in population:
        fitness = eval_home_row(genotype, frequency)
        fitness += eval_distance(genotype, frequency)
        fitness += eval_fingers(genotype, frequency)
        fitnesses.append(fitness)
    return fitnesses


def eval_distance(genotype, frequency):
    score = 0
    for index, char in enumerate(genotype):
        if 11 <= index <= 14 or 17 <= index <= 21:
            score += frequency.get(char, 0)
    return score


def eval_fingers(genotype, frequency):
    fingers = []
    fingers_iter = itertools.zip_longest(genotype[:11], genotype[11:22], genotype[22:], fillvalue=None)
    for finger in fingers_iter:
        score = 0
        for char in finger:
            score += frequency.get(char, 0)
        fingers.append(score)
    # Merge both left index columns
    finger = fingers.pop(4)
    fingers[3] += finger
    # Merge both right index columns
    finger = fingers.pop(7)
    fingers[6] += finger
    total = sum(fingers)
    expected = total / 8
    score = 0
    for finger in fingers:
        if abs(finger - expected) / expected < 0.02:
            score += 1
    return score

def select_genotypes(population, fitnesses, n):
    zipped = zip(population, fitnesses)
    sorted_list = sorted(zipped, key=lambda x: x[1], reverse=True)
    return list(zip(*sorted_list))[0][:n]


def generate_genotype():
    return random.sample(chars, len(chars))


def generate_population(size):
    population = []
    for i in range(size):
        population.append(generate_genotype())
    return population


def eval_home_row(genotype, frequency):
    home_row = genotype[11:22]
    score = 0
    for char in home_row:
        score += frequency.get(char, 0)
    return score


if __name__ == "__main__":
    main()
