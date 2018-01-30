#!/usr/bin/python3.5
# -*-coding:Utf-8 -*

import random
import operator
import time
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import functools
import matplotlib.cm as cmx

temps1 = time.time()


# genetic algorithm function
def generate_one_item(Max_weight, Max_value):
    item = []
    item.append(round(Max_weight * random.random()))
    item.append(round(Max_value * random.random()))
    return item


def generate_all_items(Number_of_item, Max_weight, Max_value):
    list_item = []
    for i in range(Number_of_item):
        list_item.append(generate_one_item(Max_weight, Max_value))
    return list_item


def total_weight_of_item_set(item_set):
    total_weight = 0
    for item in item_set:
        total_weight += item[0]
    return total_weight


def generate_one_individual(item_set):
    individual = []
    for i in range(len(item_set)):
        if (100 * random.random() < 50):
            individual.append(True)
        else:
            individual.append(False)
    return individual


def generate_first_population(item_set, size_of_population):
    population = []
    for i in range(size_of_population):
        population.append(generate_one_individual(item_set))
    return population


def weight_of_individual(individual, item_set):
    weight = 0
    for i in range(len(individual)):
        if (individual[i]):
            weight += item_set[i][0]
    return weight


def value_of_individual(individual, item_set):
    value = 0
    for i in range(len(individual)):
        if (individual[i]):
            value += item_set[i][1]
    return value


def value(individual, item_set):
    Knapsack_Capacity = round(total_weight_of_item_set(item_set) / 2)
    result = 0
    if (weight_of_individual(individual, item_set) <= Knapsack_Capacity):
        result = value_of_individual(individual, item_set)
    return result


def fitness(individual, item_set):
    Knapsack_Capacity = round(total_weight_of_item_set(item_set) / 2)
    result = 0
    if (weight_of_individual(individual, item_set) <= Knapsack_Capacity):
        result = 2 * value_of_individual(individual, item_set) - weight_of_individual(individual, item_set)
    return result


def compare(individual1, individual2):
    return fitness(individual2, item_set) - fitness(individual1, item_set)


def sort_population_by_fitness(population, item_set):
    populationSorted = sorted(population, key=functools.cmp_to_key(compare))
    return populationSorted


def select_breeders(population_sorted, size_of_population):
    result = []
    best_individuals = int(size_of_population / 5)
    lucky_few = int(size_of_population / 5)
    for i in range(best_individuals):
        result.append(population_sorted[i])
    for i in range(lucky_few):
        result.append(random.choice(population_sorted))
    random.shuffle(result)
    return result


def create_child(individual1, individual2):
    result = []
    for i in range(len(individual1)):
        if (100 * random.random() < 50):
            result.append(individual1[i])
        else:
            result.append(individual2[i])
    return result


def create_children(breeders, number_of_child):
    result = []
    for i in range(int(len(breeders) / 2)):
        for j in range(number_of_child):
            result.append(create_child(breeders[i], breeders[len(breeders) - 1 - i]))
    return result


def mutate_one_individual(individual):
    i = int(len(individual) * random.random())
    individual[i] = not individual[i]


def mutate_one_individual(individual, mutationRate):
    for geneIndex in range(len(individual)):
        if (100 * random.random() < mutationRate):
            individual[geneIndex] = not individual[geneIndex]
    return individual


def mutate_population(population, mutationRate):
    for individual in population:
        individual = mutate_one_individual(individual, mutationRate)
    return (population)


def evolve_several_generation_with_limited_time(item_set, size_of_population, number_of_child, time_limit,
                                                mutationRate):
    temps_init = time.time()
    value0 = 0
    result = []
    population = generate_first_population(item_set, size_of_population)
    value0 = max(value0, value(get_best_individual_in_population(population), item_set))
    result.append(value0)
    while (time.time() - temps_init < time_limit):
        population_sorted = sort_population_by_fitness(population, item_set)
        breeders = select_breeders(population_sorted, size_of_population)
        population = create_children(breeders, number_of_child)
        population = mutate_population(population, mutationRate)
        population = sort_population_by_fitness(population, item_set)
        value0 = max(value0, value(get_best_individual_in_population(population), item_set))
    return value0


# analysis tools
def get_best_individual_in_population(populationSorted):
    print(populationSorted[0])
    return populationSorted[0]


# print result:
def mean_result_evolve(item_set, size_of_population, number_of_child, number_of_sample, mutationRate, time_limit):
    meanResult = 0
    for i in range(number_of_sample):
        meanResult += evolve_several_generation_with_limited_time(item_set, size_of_population, number_of_child,
                                                                  time_limit, mutationRate)
    return (meanResult / number_of_sample)


def print_graph(number_of_child, number_of_sample, time_limit, item_set):
    plt.title("Algorithm efficiency with population size")
    plt.ylabel('Algorithm result')
    plt.xlabel('Population size')
    graphX = []
    graphY = []
    for i in range(19):
        size_of_population = 5 * (i + 1)
        print(size_of_population)
        mutationRate = 0
        graphX.append(size_of_population)
        graphY.append(mean_result_evolve(item_set, size_of_population, number_of_child, number_of_sample, mutationRate,
                                         time_limit))
    plt.plot(graphX, graphY)
    plt.show()


# variables
# Knapsack_Capacity = item_set_total_weight / 2
Number_of_item = 500
Max_value = 10
Max_weight = 10

number_of_child = 5
time_limit = 0.25
number_of_sample = 10

# main
item_set = generate_all_items(Number_of_item, Max_weight, Max_value)
print_graph(number_of_child, number_of_sample, time_limit, item_set)

print (time.time() - temps1)