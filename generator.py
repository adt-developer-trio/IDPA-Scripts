import random
import json
import itertools
import copy
from algorithms import *

chars = list('abcdefghijklmnopqrstuvwxyzäöü')
ITERATIONS = 400
POPULATION_SIZE = 200
SELECTED_COUNT = 50
MUTATION_COUNT = 500
MUTATION_RATE = 0.1

LAYOUT_TEMPLATE = [
    [["§", "°"], ["1", "+", "|"], ["2","\"", "@"], ["3", "*", "#"], ["4", "ç"], ["5", "%"], ["6", "&", "¬"], ["7", "/", "|"], ["8", "(", "¢"], ["9", ")"], ["0", "="], ["'", "?", "´"], ["^", "`", "~"], "Backspace"],
    ["Tab", None, None, None, None, None, None, None, None, None, None, [None, "è", "["], ["¨", "!", "]"], "Enter"],
    ["Caps Lock", None, None, None, None, None, None, None, None, None, [None, "é"], [None, "à", "{"], ["$", "£", "}"]],
    ["Shift", ["<", ">", "\\"], None, None, None, None, None, None, None, [",", ";"], [".", ":"], ["-", "_"], "Shift"],
    ["Ctrl", "Meta", "Alt", " ", "Alt Gr", "", "", "Ctrl"]
]


def main():
    population = generate_population(POPULATION_SIZE)

    with open('output/de/de.json') as file:
        data = json.load(file)
        frequency = data.get('single')
        combinations = data.get('combinations')

    for i in range(1, ITERATIONS + 1):
        fitnesses = evaluate_population(population, frequency, combinations)
        print(f'Iteration: {i} Highest fitness: {max(fitnesses)}')
        selected = select_genotypes(population, fitnesses, SELECTED_COUNT)
        mutated = mutate(selected, MUTATION_RATE, MUTATION_COUNT)
        new_count = POPULATION_SIZE - MUTATION_COUNT - SELECTED_COUNT
        new_gen = generate_population(new_count)
        population = list(selected) + mutated + new_gen
    else:
        best = population[fitnesses.index(max(fitnesses))]
        print_layout(best)
        print(f'Finger distance: {finger_distance(best, frequency)[1]}')
        print(f'Finger distribution: {finger_distribution(best, frequency)[1]}')
        print(f'Row dist: {row_distribution(best, frequency)[1]}')
        print(f'Combinations: {combination_occurrences(best, combinations)[1]}')


def print_layout(genotype):
    for row in genotype:
        print(row)


def mutate_char(char, char_list, rate):
    new_char_list = char_list[:]
    if random.random() < rate/100:
        index1 = new_char_list.index(char)
        index2 = random.randint(0, len(new_char_list) - 1)
        new_char_list[index1], new_char_list[index2] = new_char_list[index2], new_char_list[index1]
    return new_char_list


def extract_chars(layout):
    char_list = []
    for r, row in enumerate(layout):
        for i, key in enumerate(row):
            if LAYOUT_TEMPLATE[r][i] is None:
                char_list.append(layout[r][i])
            elif isinstance(LAYOUT_TEMPLATE[r][i], list):
                for l, layer in enumerate(key):
                    if LAYOUT_TEMPLATE[r][i][l] is None:
                        char_list.append(layout[r][i][l])
    return char_list


def layout_from_chars(char_list):
    layout = copy.deepcopy(LAYOUT_TEMPLATE)
    for r, row in enumerate(layout):
        for i, key in enumerate(row):
            if key is None:
                layout[r][i] = char_list.pop(0)
            if isinstance(key, list):
                for l, layer in enumerate(key):
                    if layout[r][i][l] is None:
                        layout[r][i][l] = char_list.pop(0)
    return layout


def mutate(selected, rate, n):
    mutated = []
    source = itertools.cycle(selected)
    for i in range(n):
        genotype = next(source)[:]
        char_list = extract_chars(genotype)
        for i in range(len(char_list)):
            if random.random() < rate:
                index = random.randint(0, len(char_list) - 1)
                char_list[i], char_list[index] = char_list[index], char_list[i]
        mutated.append(layout_from_chars(char_list))
    return mutated


def evaluate_population(population, frequency, combinations):
    fitnesses = []
    for genotype in population:
        fitness = finger_distance(genotype, frequency)[1]
        fitness += finger_distribution(genotype, frequency)[1]
        fitness += row_distribution(genotype, frequency)[1]
        fitness += combination_occurrences(genotype, combinations)[1]
        fitnesses.append(fitness)
    return fitnesses


def select_genotypes(population, fitnesses, n):
    zipped = zip(population, fitnesses)
    sorted_list = sorted(zipped, key=lambda x: x[1], reverse=True)
    return list(zip(*sorted_list))[0][:n]


def generate_genotype():
    random_chars = random.sample(chars, len(chars))[:]
    layout = layout_from_chars(random_chars)
    return layout


def generate_population(size):
    population = []
    for i in range(size):
        population.append(generate_genotype())
    return population


if __name__ == "__main__":
    main()
