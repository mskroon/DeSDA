from collections import Counter
from nltk.corpus import stopwords
from math import log
import numpy as np
from fasttext_translator import calculate_transformation_matrix
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
import scipy.stats

def Sen_vec_cossim(data_file, train_dict, M1, M2, removestopwords=False, tfidf=False, geometric=False):
    print('Sentence vectors:')
    print('\tRemovestopwords:', removestopwords)
    print('\ttf-idf:', tfidf)
    print('\tGeometric mean:', geometric)

    value = []
    target = []
    model1 = fasttext.load_model(M1, encoding='utf-8')
    model2 = fasttext.load_model(M2, encoding='utf-8')
    W = calculate_transformation_matrix(model1, model2, train_dict)
    if removestopwords:
        model1stopwords = stopwords.words('english')
        model2stopwords = stopwords.words('dutch')
    if tfidf:
        # calculate idfs
        print('Calculating idf values...')
        model1_idf = {}
        model2_idf = {}
        nr_sentences = 0
        with open(data_file, 'r') as TRAIN:
            for line in TRAIN:
                nr_sentences += 1
                line = line[:-1].split('\t')
                line[1] = {w.split('|')[0] for w in line[1].split()}
                line[2] = {w.split('|')[0] for w in line[2].split()}
                for w in line[1]:
                    model1_idf[w] = model1_idf.get(w, 0) + 1
                for w in line[2]:
                    model2_idf[w] = model2_idf.get(w, 0) + 1
            for w, count in model1_idf.items():
                model1_idf[w] = log(nr_sentences / count)
            for w, count in model2_idf.items():
                model2_idf[w] = log(nr_sentences / count)
    with open(data_file, 'r') as DATA:
        for line in DATA:
            line = line[:-1].split('\t')
            line[1] = [w.split('|')[0] for w in line[1].split()]
            line[2] = [w.split('|')[0] for w in line[2].split()]
            if removestopwords:
                line[1] = [w for w in line[1] if w not in model1stopwords]
                line[2] = [w for w in line[2] if w not in model2stopwords]
            if tfidf:
                line1_counter = Counter(line[1])
                line2_counter = Counter(line[2])
                line[1] = [np.array([W.dot(model1[w])])*(line1_counter[w]/len(line[1]))*model1_idf[w] for w in line[1]] # dot product with W: sane as in word2vec_translation.py
                line[2] = [np.array([model2[w]])*(line2_counter[w]/len(line[2]))*model2_idf[w] for w in line[2]]
            else:
                line[1] = [np.array([W.dot(model1[w])]) for w in line[1]]
                line[2] = [np.array([model2[w]]) for w in line[2]]

            if geometric:
                line[1] = scipy.stats.mstats.gmean(np.array(line[1])**2)**.5
                line[2] = scipy.stats.mstats.gmean(np.array(line[2])**2)**.5
                # line[1] = product(line[1]) ** (1/len(line[1]))
                # print(line[1])
                # line[2] = product(line[2]) ** (1/len(line[2]))
            else:
                line[1] = np.mean(line[1], axis=0)
                line[2] = np.mean(line[2], axis=0)
                # line[1] = sum(line[1]) / len(line[1])
                # line[2] = sum(line[2]) / len(line[2])
            # print(line)
            d = float(cosine_similarity(line[1], line[2]))
            value.append(d)
            target.append(line[0])
    print()
    return list(zip(value, target))