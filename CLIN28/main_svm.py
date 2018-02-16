import levenshtein
import senlen_ratio
import zhang_shasha_UD
import senvec
import networkx_GED
import numpy as np
from sklearn.svm import LinearSVC, SVC
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from itertools import combinations
import random
from collections import Counter

data = '/vol/home/kroonms/DeSDA/CLIN28/en-nl.syn.train'
udM1 = '/vol/home/kroonms/Downloads/udpipe-ud-2.0-conll17-170315/models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
udM2 = '/vol/home/kroonms/Downloads/udpipe-ud-2.0-conll17-170315/models/dutch-ud-2.0-conll17-170315.udpipe' #a UDPipe model
train_dict = '/vol/home/kroonms/DeSDA/CLIN28/en-nl.basicwordlist.csv'
svM1 = 'model1.bin' #a fastText model for English (files too big to be on GitHub)
svM2 = 'model2.bin' #a fastText model for Dutch


Methods = [
    ('lev', levenshtein.Levenshtein(data, removestopwords=False)),
    ('senlen', senlen_ratio.Senlen_ratio(data, removestopwords=False)),
    ('ud', zhang_shasha_UD.Zhang_Shasha_UD(data, udM1, udM2, ignore_morphology=False, removestopwords=False)),
    ('nx_ged_im', networkx_GED.Networkx_GED(data, udM1, udM2, ignore_morphology=True)),
    ('senvec_tf_rm', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=True, tfidf=True)),
]

M = []
for i in range(1, len(Methods) + 1):
    C = list(combinations(Methods, i))
    M += C
for methods in M:
    print([m[0] for m in methods])

    full_data_values = np.array(list(zip(*[[s[0] for s in m[1]] for m in methods])))
    # print(full_data_values)
    full_data_target = np.array([l[1] for l in methods[0][1]])
    # print(full_data_target)

    #cross_validation:
    classifier = LinearSVC()
    scores = cross_val_score(classifier, full_data_values, full_data_target, cv=10, scoring='f1_macro')
    print("F1: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    #normal
    # train_values, test_values, train_target, test_target = train_test_split(full_data_values, full_data_target, test_size=0.5)
    # classifier.fit(train_values, train_target)
    # print(list(zip([x[0] for x in methods], classifier.coef_[0])))
    # print(classification_report(test_target, classifier.predict(test_values)))
    # print(confusion_matrix(test_target, classifier.predict(test_values), labels=['Y', 'N']))