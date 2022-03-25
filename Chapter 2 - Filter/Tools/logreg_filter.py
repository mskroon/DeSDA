import levenshtein
import senlen_ratio
import networkx_GED
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import label_binarize


input_file = '../Data/de-en.train'
udM1 = '../Data/UDPipe_models/german-ud-2.0-conll17-170315.udpipe' #a UDPipe model
udM2 = '../Data/UDPipe_models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
output_file = '../Output/de-en.raw.filtered'


'''senlen parameters'''
use_sentence_length = True
senlen_removestopwords = True
senlen_stopwords = ['ADP']

'''levenshtein parameters'''
use_levenshtein = True
lev_removestopwords = True
lev_stopwords = ['CCONJ', 'NUM', 'PART']
lev_transposition = False

'''GED parameters'''
use_GED = False
ged_removestopwords = True
ged_stopwords = ['NUM', 'SCONJ']



methods = []
if use_sentence_length:
    senlen = senlen_ratio.Senlen_ratio((input_file, senlen_removestopwords, senlen_stopwords))
    methods.append(senlen)
if use_levenshtein:
    lev = levenshtein.Levenshtein((input_file, lev_removestopwords, lev_stopwords, lev_transposition))
    methods.append(lev)
if use_GED:
    ged = networkx_GED.Networkx_GED((input_file, udM1, udM2, ged_removestopwords, ged_stopwords))
    methods.append(ged)


label = tuple(m[0] for m in methods)
full_data_values = np.array(list(zip(*[[s[0] for s in m[1]] for m in methods])))
full_data_target = np.array([l[1] for l in methods[0][1]])

full_data_target = label_binarize(full_data_target, classes=['Y', 'N'])
clf = LogisticRegression().fit(full_data_values, full_data_target)
pred = clf.predict(full_data_values)

with open(input_file, 'r') as input_file, open(output_file, 'w') as output_file:
    for sentence_pair, prediction in zip(input_file, pred):
        if prediction == 0:
            sentence_pair = '\t'.split(sentence_pair, 1)
            output_file.write(sentence_pair)