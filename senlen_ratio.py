from nltk.corpus import stopwords
from math import log

def ratio(a, b):
    return 2**abs(log(a/b, 2))

def Senlen_ratio(data_file, removestopwords=False):
    print('Sentence-length ratio:')
    print('\tRemove stopwords:', removestopwords)
    value = []
    target = []
    if removestopwords:
        model1stopwords = stopwords.words('english')
        model2stopwords = stopwords.words('dutch')
    with open(data_file, 'r') as DATA:
        for line in DATA:
            line = line[:-1].split('\t')
            if removestopwords:
                line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[0] not in model1stopwords]
                line[2] = [w.split('|')[1] for w in line[2].split() if w.split('|')[0] not in model2stopwords]
            else:
                line[1] = [w.split('|')[1] for w in line[1].split()]
                line[2] = [w.split('|')[1] for w in line[2].split()]
            d = ratio(len(line[1]), len(line[2]))
            value.append(d)
            target.append(line[0])
    print()
    return list(zip(value, target))