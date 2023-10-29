import csv
import sys

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot(rdf, file, ymin=None, ymax=None):
    if len(rdf) == 0:
        print("failed")
        return

    if 'provider' in rdf.columns:
        grdf = rdf.groupby(['nextHopProtocol', 'provider'])
    else:
        grdf = rdf.groupby(rdf['nextHopProtocol'])

    plt.figure(figsize=(7, 5))
    labels = list()
    for name, group in grdf:
        sns.lineplot(data=group, x="encodedBodySize", y="duration", estimator="median", errorbar=("pi", 50))
        labels.append("[" + str(name[1]) + '] duration in ms')
        labels.append("[" + str(name[1]) + '] error duration in ms')
        #sns.lineplot(data=group, x="encodedBodySize", y="connectDuration", estimator="median", errorbar=("pi", 50))
        #labels.append("[" + str(name) + '] connect in ms')
    plt.legend(labels=labels, loc='upper left')
    if ymax is not None:
        plt.ylim(0, int(ymax))
    plt.xscale('log')

    if file == '':
        plt.show()
    else:
        plt.savefig(file)

