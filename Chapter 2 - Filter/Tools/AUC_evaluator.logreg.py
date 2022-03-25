import levenshtein
import senlen_ratio
import networkx_GED
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import label_binarize
from itertools import product, compress, chain
import multiprocessing
ncores = int(multiprocessing.cpu_count()-1)
ncores = 1

data = '../Data/de-en.train'
udM1 = '../Data/UDPipe_models/german-ud-2.0-conll17-170315.udpipe' #a UDPipe model
udM2 = '../Data/UDPipe_models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
# SYM and X are not present in this particular data, so can be removed from closed_set:
# closed_set = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
closed_set = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ']


def DoThings(methods):
    label = tuple(m[0] for m in methods)
    full_data_values = np.array(list(zip(*[[s[0] for s in m[1]] for m in methods])))
    full_data_target = np.array([l[1] for l in methods[0][1]])
    full_data_target = label_binarize(full_data_target, classes=['Y', 'N'])
    clf = LogisticRegression().fit(full_data_values, full_data_target)
    prob = clf.predict_proba(full_data_values)
    prob = prob.T[1]
    auc = roc_auc_score(full_data_target, prob)
    return (label, round(auc, 5))


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=ncores)
    # data_file, removestopwords, stopwords = pars
    senlen = product((data,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))])
    senlen = pool.map(senlen_ratio.Senlen_ratio, senlen)
    pool.close()

    pool = multiprocessing.Pool(processes=ncores)
    # data_file, removestopwords, stopwords, transposition = pars
    lev = product((data,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))], (True, False))
    lev = pool.map(levenshtein.Levenshtein, lev)
    pool.close()

    pool = multiprocessing.Pool(processes=ncores)
    # data_file, M1, M2, removestopwords, stopwords = pars
    ged = product((data,), (udM1,), (udM2,), (True, ), [list(compress(closed_set, C)) for C in product([0,1], repeat=len(closed_set))])
    ged = pool.map(networkx_GED.Networkx_GED, ged)
    pool.close()


    M = product(lev)
    M = chain(M, product(senlen))
    M = chain(M, product(ged))
    M = chain(M, product(lev, senlen))
    M = chain(M, product(lev, ged))
    M = chain(M, product(senlen, ged))
    M = chain(M, product(lev, senlen, ged))


    pool = multiprocessing.Pool(processes=ncores)
    results = pool.map(DoThings, M)
    pool.close()

    results_dict = {}
    for m in results:
        results_dict[m[1]] = results_dict.get(m[1], [])
        results_dict[m[1]].append(m[0])
    for v, k in sorted(results_dict.items(), key=lambda x: x[0]):
        print(v, sorted(k, key=len))