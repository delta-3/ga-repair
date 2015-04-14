#!/usr/bin/env python
import re
import sys
import random
import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

escaped = ['\d', '\D', '\w', '\W']
#VALID_CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,*+?{}[]()") + escaped
ALPHANUMERIC = map(chr,range(65,91)) + map(chr,range(97,123)) + map(str,range(0,10))
VALID_CHARS = list("+*[]") + escaped # + ALPHANUMERIC
MAX_LENGTH = 20
MIN_LENGTH = 5
def read_data(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
        return lines


def get_random_char():
    r = random.randint(0, len(VALID_CHARS)-1)
    return VALID_CHARS[r]

def gen_filter(min, max):
    l = random.randint(min, max)
    return [get_random_char() for i in range(l)]
        
def evalFilter(individual):
    '''
    Filter should include good input and not bad input
    '''
    matches = 0
    pattern = "".join(individual)
    for evil in DATA_EVIL:
        for good in DATA_BENIGN:
            #print "Testing pattern ", pattern 
            try:
                if re.search(pattern, good) and not re.search(pattern, evil):
                    matches+=1

            except:
                return 10000,
    print "total matches %d for %s" % (matches, pattern)
    return abs(len(DATA_BENIGN) + len(DATA_EVIL) - matches),

def eval2(ind):
    pattern = "^" + "".join(ind) + "$"
    sB=0
    sE =0
#Need to make sure if there is a opening there is also a closing
    if pattern.count("[") != 0 and pattern.count("]") == 0:
        sB = 5
        sE = 5
    for evil in DATA_EVIL:
        try:
            if re.match(pattern, evil):
                sE+=100
            else:
                sE-=1
        except:
            sE+=100

    for good in DATA_BENIGN:
        try:
            if re.match(pattern, good):
                sB-=1
            else:
                sB+=1
        except:
            sB+=100
    return abs(len(DATA_BENIGN) + sB),abs(len(DATA_EVIL) + sE),len(pattern),

def mutAddFilter(ind):
    c = get_random_char()
    ind.append(c)
    return ind,

def mutDelFilter(ind):
    pos = random.randint(0, len(ind)-1)
    if not ind:
        ind.pop(pos)
    return ind,

def mut(individual):
    c = get_random_char()
    pos = random.randint(0, len(individual)-1)
    individual[pos] = c
    return individual, 

def mate(ind1, ind2):
    
    for i in range(min(len(ind1), len(ind2))):
        if random.random() < 0.5:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2

creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0,-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_item", get_random_char)

toolbox.register("word", gen_filter, MIN_LENGTH, MAX_LENGTH)
# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.word)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# Operator registering
toolbox.register("evaluate",eval2)
toolbox.register("mate", mate)
toolbox.register("mutate",mut)
toolbox.register("addFilter", mutAddFilter)
toolbox.register("delFilter", mutDelFilter)
toolbox.register("select",tools.selBest )

def main():
    random.seed(64)

    CXPB, MUTPB, ADDPB, DELPB, MU, NGEN = 0.7, 0.4, 0.4, 0.4, 200, 1000

    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max", "best"
    
    # Evaluate every individuals
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    hof.update(pop)
    record = stats.compile(pop)
    logbook.record(gen=0, evals=len(pop), **record)
    print(logbook.stream)

    gen = 1
    while gen <= NGEN:# and logbook[-1]["max"] != 0.0:
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
    
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
            if random.random() < ADDPB:
                toolbox.addFilter(mutant)
                del mutant.fitness.values
            if random.random() < DELPB:
                toolbox.delFilter(mutant) 
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        b = tools.selBest(pop, k=1)[0]
        w = "".join(b) 
        
        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), best=w, **record)
        print(logbook.stream)

        gen += 1

    return pop, logbook

if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    DATA_EVIL = read_data(f1)
    DATA_BENIGN = read_data(f2)
    pop, stats = main() 
    b = tools.selBest(pop, k=1)[0]
    print "".join(b)

