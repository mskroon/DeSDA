import levenshtein
import senlen_ratio
import networkx_GED
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.preprocessing import label_binarize
from itertools import compress, product
import multiprocessing
ncores = int(multiprocessing.cpu_count()-1)


data = '../Data/de-en.train'
udM1 = '../Data/UDPipe_models/german-ud-2.0-conll17-170315.udpipe' #a UDPipe model
udM2 = '../Data/UDPipe_models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
# SYM and X are not present in this particular data, so can be removed from closed_set:
# closed_set = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
closed_set = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ']



methods = []
if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=ncores)
    # data_file, removestopwords, stopwords = pars
    senlen = product((data,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))])
    senlen = pool.map(senlen_ratio.Senlen_ratio, senlen)
    pool.close()
    methods += list(senlen)

    pool = multiprocessing.Pool(processes=ncores)
    # data_file, removestopwords, stopwords, transposition = pars
    lev = product((data,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))], (True, False))
    lev = pool.map(levenshtein.Levenshtein, lev)
    pool.close()
    methods += list(lev)

    pool = multiprocessing.Pool(processes=ncores)
    # data_file, M1, M2, removestopwords, stopwords = pars
    ged = product((data,), (udM1,), (udM2,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))])
    ged = pool.map(networkx_GED.Networkx_GED, ged)
    pool.close()
    methods += list(ged)


    results = []
    for label, method in methods:
        print(label)
        auc_above = roc_auc_score(label_binarize([p[1] for p in method], classes=['N', 'Y']), [p[0] for p in method])
        auc_below = roc_auc_score(label_binarize([p[1] for p in method], classes=['Y', 'N']), [p[0] for p in method])
        if auc_above > auc_below:
            roc = roc_curve(label_binarize([p[1] for p in method], classes=['N', 'Y']), [p[0] for p in method])
            label += '>'
            auc = round(auc_above, 5)
        else:
            roc = roc_curve(label_binarize([p[1] for p in method], classes=['Y', 'N']), [p[0] for p in method])
            label += '<'
            auc = round(auc_below, 5)
        # plt.plot(roc[0], roc[1], '-', label=label)
        roc = list(zip(*roc))
        print('\tAUC:', auc)
        results.append((label, auc))
        print('\tYouden:', max(roc, key=lambda x: x[1]-x[0]))
        print('\tEuclidean:', min(roc, key=lambda x: ((x[0]**2 + (1-x[1]**2))**.5)))
    results_dict = {}
    for m in results:
        results_dict[m[1]] = results_dict.get(m[1], [])
        results_dict[m[1]].append(m[0])
    results = sorted(results_dict.items(), key=lambda x: x[0])
    for v, k in results:
        print(v, sorted(k, key=len))


    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.axis([0, 1, 0, 1])
    # plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()
