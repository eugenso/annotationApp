from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import json
import os

def readRunFile(mark):
    """Returns a dict"""
    runNames = []
    for file in os.listdir('data'):
        nameBits = file.split('_')
        if file.startswith('run_') and file.endswith('.json') and nameBits[2] == mark:
            runNames.append((nameBits[1], file))
            #
    runNames.sort(key=itemgetter(0))
    runs = []
    for runName in map(itemgetter(1), runNames):
        with open(os.path.join('data', runName), 'r') as runFile:
            runs.append(json.load(runFile))
            #
    return runs


def processJSONtoPLOT(runs):
    accuracies = []
    sortRunFn = lambda run: map(lambda k: run[str(k)], sorted(map(int, run.keys())))
    for run in runs:
        # sort run according to keys
        sortRun = sortRunFn(run)
        # select accuracy from every step
        accuracies.append(map(lambda step:step['accuracy'], sortRun))
        #
    # zip the accuracies for the same step over the different runs together
    sortAccuracies = zip(*accuracies)
    #
    stdAccuracies = map(np.std, sortAccuracies)
    meanAccuracies = map(np.mean, sortAccuracies)
    #
    steps = map(lambda s: s['step'], sortRunFn(runs[0]))
    X = reduce(lambda x, s: x+[x[-1]+s], steps[1:], [steps[0]])

    return X, meanAccuracies, stdAccuracies

def plotCurve():
    #
    XR, meanAccRandom, stdAccRandom = processJSONtoPLOT(readRunFile('R'))
    XA, meanAccActive, stdAccActive = processJSONtoPLOT(readRunFile('A'))
    #
    plt.figure()
    plt.errorbar(XR, meanAccRandom, yerr=stdAccRandom,
                 fmt='s', markersize=5, linewidth=2, label='Random order')
    plt.errorbar(XA, meanAccActive, yerr=stdAccActive,
                 fmt='o', markersize=5, linewidth=2, label='Minimal margin sampling')
    axes = plt.gca()
    axes.set_xlim([0,260])
    plt.xlabel('Number of training instances')
    plt.ylabel('Accuracy')
    plt.legend(loc=4)
    plt.show()


plotCurve()
