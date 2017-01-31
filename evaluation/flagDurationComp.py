from __future__ import division
from Annotation import Annotation
from itertools import groupby
from operator import itemgetter
from createTable import tableBuilder

import numpy as np
import matplotlib.pylab as plt
import scipy.stats
import seaborn as sns; sns.set(color_codes=True, style="whitegrid")


def bayesian_information_criterion(ll,k,n):
    return -2.0 * ll + k * np.log(n)


A = Annotation('data/exportMedium.json')

key = itemgetter('proposalFlag')


fD = dict((flag, A.durationToSec(map(itemgetter('duration'), annotations)))
          for flag, annotations in groupby(sorted(A.all, key=key), key=key))

labels=['proposal', 'no proposal', 'wrong proposal']

distributions = ['betaprime',
                #'burr',
                #'chi',
                'chi2',
                #'erlang',
                'expon',
                #'exponweib',
                #'exponpow',
                #'f',
                #'fatiguelife',
                #'fisk',
                #'frechet_r',
                'gamma',
                #'genpareto',
                #'genexpon',
                #'gompertz',
                #'halflogistic',
                #'halfnorm',
                #'halfgennorm',
                #'invgamma',
                #'lognorm',
                #'maxwell',
                #'mielke',
                #'ncx2',
                #'ncf',
                #'recipinvgauss',
                #'wald'
]

rlts = {}

for label in labels:
    rlts[label] = []
    data = np.array(fD[label])
    for distribution in distributions:
        dist = getattr(scipy.stats, distribution)
        params = dist.fit(data, loc=0)
        logLikelihood = dist.logpdf(data, *params).sum()
        bic = bayesian_information_criterion(
            logLikelihood, len(params), data.shape[0])
        rlts[label].append([logLikelihood, bic, params])

# for label in labels:
#     print 'result:', np.array(rlts[label])

table = [['BIC']+distributions]
for label in labels:
    rlt = np.array(map(lambda x: x[:2], rlts[label]))
    idx = rlt[:, 1].argmin()
    dist = getattr(scipy.stats, distributions[idx])
    print 'Best distribution for {}:'.format(label), dist.name
    # append row
    table.append([label]+map(lambda x: str(round(x*100)/100), rlt[:, 1]))

tB = tableBuilder()
tB.createSimpleTable(zip(*table), True, '/home/kai/Dropbox/MA/thesis/table/BIC.tex')


dom = np.linspace(0,200,1000)

c = {'no proposal': 'g',
     'proposal': 'b',
     'wrong proposal': 'r'}

fig = plt.Figure()

for label in labels:
    data = np.array(fD[label])
    rlt = np.array(map(lambda x: x[:2], rlts[label]))
    idx = rlt[:, 1].argmin()
    dist = getattr(scipy.stats, distributions[idx])
    params = rlts[label][idx][2]
    mean, var = dist.stats(*params)
    plt.plot([mean, mean],
             [0, dist.pdf(mean, *params)],
             linewidth=3,
             c=c[label])
    plt.plot(dom,
             dist.pdf(dom, *params),
             linewidth=3,
             label='{:{}} Mean: {}'.format(label, len(labels[2]), str(round(mean*1000)/1000)),
             c=c[label])

x1,x2,y1,y2 = plt.axis()
plt.axis((0,150,0,y2))

plt.xlabel('Duration in sec', fontsize=12)
plt.ylabel('Density', fontsize=12)

plt.legend(loc='best', prop={'size':12}, frameon=True)

plt.savefig('/home/kai/Dropbox/MA/thesis/img/flagDurationComp.pdf',
            bbox_inches='tight',
            format='pdf')


plt.show()


npn_stat, npn_pvalue = scipy.stats.mannwhitneyu(fD['proposal'], fD['no proposal'],
                                                alternative='two-sided')

pwp_stat, pwp_pvalue = scipy.stats.mannwhitneyu(fD['proposal'], fD['wrong proposal'],
                                                alternative='two-sided')

npwp_stat, npwp_pvalue = scipy.stats.mannwhitneyu(fD['no proposal'], fD['wrong proposal'],
                                                   alternative='two-sided')

table = [['', 'proposal', 'no proposal', 'wrong proposal'],
         ['proposal', '', '{}, {}'.format(npn_stat, npn_pvalue), '{}, {}'.format(pwp_stat, pwp_pvalue)],
         ['no proposal', '', '', '{}, {}'.format(npwp_stat, npwp_pvalue)],
         ['wrong proposal', '', '', '']]

tB.createSimpleTable(table, True, '/home/kai/Dropbox/MA/thesis/table/mannwhiteyu.tex')
