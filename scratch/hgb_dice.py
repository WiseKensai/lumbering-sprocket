#!/usr/bin/python3

import random
import numpy
import collections
import matplotlib.pyplot as plt

doGraph = True
try:
    import plotille
except ImportError:
    doGraph = False

def roll_dice(dice,skill):
    rolls = [random.randrange(1,7) for i in range(dice)]
    base = max(rolls)
    rolls.remove(base)
    return base + sum([1 if i >= skill else 0 for i in rolls])


def monte_carlo_mos(diceA,skillA,diceB,skillB,bonus,samples):
    return [roll_dice(diceA,skillA) - roll_dice(diceB,skillB) + bonus for i in range(samples)]

def process_damage(samples,dam,ar,ap=0,agile=True,fire=0):
    damage = samples
    for i in range(len(samples)):
        if samples[i] < 0:
            damage[i] = 0
        elif samples[i] == 0 and agile:
            damage[i] = 0
        else:
            cal = max(0,samples[i] + dam - ar);
            if ap > 0:
                damage[i] = max(cal,max(1,min(ap,samples[i])))
            else:
                if cal == 0:
                    damage[i] = random.randint(0,1)
                else:
                    damage[i] = cal
            for f in range(fire):
                damage[i] = damage[i] + random.randint(0,1)
    return damage

def print_results(samples):
    histogram = collections.Counter(samples)

    print("Mean: {0:3.2f}".format(sum(samples)*1.0/len(samples)))
    print("  Q1: {0}".format(numpy.quantile(samples,0.25)))
    print("  Q3: {0}".format(numpy.quantile(samples,0.75)))

    print("Val: % chance")
    for i in range(min(samples),max(samples)+1):
        print("  {0:2d}: {1:6.3f}".format(i,histogram[i]*100.0/len(samples)))

def calculate_hit(samples,agile=False):
    histogram = collections.Counter(samples)
    hit = 0
    for i in range(min(samples),max(samples)+1):
        chance = histogram[i]*100.0/len(samples)
        if i > 0:
            hit = hit + chance
        elif i == 0 and not agile:
            hit = hit + chance
    print("Chance to Hit: {0:6.3f}".format(hit))

def calculate_death(samples,hull,structure):
    histogram = collections.Counter(samples)
    cripple = 0
    kill = 0
    for i in range(min(samples),max(samples)+1):
        chance = histogram[i]*100.0/len(samples)
        if i >= hull:
            cripple = cripple + chance
        if i >= hull+structure:
            kill = kill + chance
    print("Chance to Cripple: {0:6.3f}".format(cripple))
    print("Chance to Kill:    {0:6.3f}".format(kill))



def sample_and_plot(diceA,skillA,diceB,skillB,dam,ar,ap=0,agile=False,bonus=0,fire=0,hull=4,structure=2,nsamples=10000):
    samples = monte_carlo_mos(diceA,skillA,diceB,skillB,bonus,nsamples)
    samples = [sample for sample in samples]

    print("Scenario: {0}d6 @ {1}+ versus {2}d6 @ {3}+".format(diceA,skillA,diceB,skillB))
    print("DAM = {0}, AR = {1}".format(dam,ar))
    print("Agile = {0}, Bonus = {1}, AP = {2}, H/S = {3}/{4}".format(agile,bonus,ap,hull,structure))
    print("MoS")
    print_results(samples)
    calculate_hit(samples,agile=agile)
    print("Dam")
    damage = process_damage(samples,dam,ar,ap=ap,agile=agile,fire=fire)
    print_results(damage)
    calculate_death(samples,hull,structure)


if __name__ == "__main__":
    random.seed(42)
    sample_and_plot(2,4,3,4,7,6,hull=4,structure=2,ap=1,bonus=0)
    sample_and_plot(2,4,3,4,7,6,hull=4,structure=2,ap=1,bonus=1)
