import random
import operator
import time
import matplotlib.pyplot as plt
import stringdist

temps1 = time.time()

# genetic algorithm functions
def fitness_(passwd, testWord):
    score = 0
    i = 0
    while i < len(password):
        if password[i] == testWord[i]:
            score += 1
        i += 1
    return score * 100 / len(passwd)

def fitness(passwd, testWord):
    score = stringdist.rdlevenshtein_norm(passwd, testWord)
    return (1 - score) * 100

def generateAWord(length):
    i = 0
    result = ""
    while i < length:
        letter = chr(97 + int(26 * random.random()))
        result += letter
        i += 1
    return result


def generateFirstPopulation(sizePopulation, passwd):
    population = []
    i = 0
    while i < sizePopulation:
        population.append(generateAWord(len(passwd)))
        i += 1
    return population


def computeFitnessInPopulation(population, passwd):
    populationPerf = {}
    for individual in population:
        populationPerf[individual] = fitness(passwd, individual)
    return sorted(populationPerf.items(), key=operator.itemgetter(1), reverse=True)


def selectFromPopulation(populationSorted, bestSample, luckyFew):
    nextGenerationAssembled = []
    for i in range(bestSample):
        nextGenerationAssembled.append(populationSorted[i][0])
    for i in range(luckyFew):
        nextGenerationAssembled.append(random.choice(populationSorted)[0])
    random.shuffle(nextGenerationAssembled)
    return nextGenerationAssembled


def createChild(individual1, individual2):
    child = ""
    for i in range(len(individual1)):
        if int(100 * random.random()) < 50:
            child += individual1[i]
        else:
            child += individual2[i]
    return child


def createChildren(breeders, numberOfChild):
    nextPopulation = []
    for i in range(round(len(breeders) / 2)):
        for j in range(numberOfChild):
            nextPopulation.append(createChild(breeders[i], breeders[len(breeders) - 1 - i]))
    return nextPopulation


def mutateWord(word):
    index_modification = int(random.random() * len(word))
    if index_modification == 0:
        word = chr(97 + int(26 * random.random())) + word[1:]
    else:
        word = word[:index_modification] + chr(97 + int(26 * random.random())) + word[index_modification + 1:]
    return word


def mutatePopulation(population, chanceOfMutation):
    for i in range(len(population)):
        if random.random() * 100 < chanceOfMutation:
            population[i] = mutateWord(population[i])
    return population


def nextGeneration(firstGeneration, passwd, bestSample, luckyFew, numberOfChild, chanceOfMutation):
    populationSorted = computeFitnessInPopulation(firstGeneration, passwd)
    nextBreeders = selectFromPopulation(populationSorted, bestSample, luckyFew)
    nextPopulation = createChildren(nextBreeders, numberOfChild)
    nextPopulation = mutatePopulation(nextPopulation, chanceOfMutation)
    return nextPopulation


def multipleGeneration(numberOfGeneration, passwd, sizePopulation, bestSample,
                       luckyFew, numberOfChild, chanceOfMutation):
    populations = [generateFirstPopulation(sizePopulation, passwd)]
    for i in range(numberOfGeneration):
        populations.append(
            nextGeneration(populations[i], passwd, bestSample, luckyFew, numberOfChild, chanceOfMutation))
    return populations


# print result:
def printSimpleResult(populations, passwd, numberOfGeneration):
    result = getBestIndividualsListFromAllTimes(populations, passwd)[numberOfGeneration - 1]
    print("solution: \"" + result[0] + "\" de fitness: " + str(result[1]))


# analysis tools
def getBestIndividualFromPopulation(population, passwd):
    return computeFitnessInPopulation(population, passwd)[0]

def getBestIndividualsListFromAllTimes(populations, passwd):
    bestIndividuals = []
    for population in populations:
        bestIndividuals.append(getBestIndividualFromPopulation(population, passwd))
    return bestIndividuals


# graph
def evolutionBestFitness(populations, passwd):
    plt.axis([0, len(populations), 0, 105])
    plt.title(passwd)

    evolutionFitness = []
    for population in populations:
        evolutionFitness.append(getBestIndividualFromPopulation(population, passwd)[1])
    plt.plot(evolutionFitness)
    plt.ylabel('fitness best individual')
    plt.xlabel('generation')
    plt.show()


def evolutionAverageFitness(populations, passwd, sizePopulation):
    plt.axis([0, len(populations), 0, 105])
    plt.title(passwd)

    evolutionFitness = []
    for population in populations:
        populationPerf = computeFitnessInPopulation(population, passwd)
        averageFitness = 0
        for individual in populationPerf:
            averageFitness += individual[1]
        evolutionFitness.append(averageFitness / sizePopulation)
    plt.plot(evolutionFitness)
    plt.ylabel('Average fitness')
    plt.xlabel('generation')
    plt.show()


# variables
password = "constantinopla"
# assert(best_sample + lucky_few) / 2 * number_of_child == size_population)
size_population = 100
best_sample = 30
lucky_few = 10
number_of_child = 5
number_of_generation = 100
chance_of_mutation = 5

# program
if (best_sample + lucky_few) / 2 * number_of_child != size_population:
    print("population size not stable")
else:
    all = multipleGeneration(number_of_generation,
                                  password,
                                  size_population,
                                  best_sample,
                                  lucky_few,
                                  number_of_child,
                                  chance_of_mutation)

    printSimpleResult(all, password, number_of_generation)

    evolutionBestFitness(all, password)
    #evolutionAverageFitness(all, password, size_population)