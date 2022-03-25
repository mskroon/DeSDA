from scipy.stats import percentileofscore

def ratio(a, b):
    if b == 0:
        return 0
    return a/b


def Senlen_ratio(pars):
    data_file, removestopwords, stopwords = pars
    # print('Sentence-length ratio:')
    # print('\tRemove stopwords:', removestopwords)
    # print('\tStopwords:', stopwords)
	
    value = []
    target = []
    if removestopwords:
        if stopwords is None:
            stopwords = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
    with open(data_file, 'r') as DATA:
        for line in DATA:
            line = line[:-1].split('\t')
            if removestopwords:
                line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
                line[2] = [w.split('|')[1] for w in line[2].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
            else:
                line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1]!='PUNCT']
                line[2] = [w.split('|')[1] for w in line[2].split() if w.split('|')[1]!='PUNCT']
            d = ratio(len(line[1]), len(line[2]))
            value.append(d)
            target.append(line[0])
    percentiles = []
    for v in value:
        p = percentileofscore(value, v)
        if p < 50:
            percentiles.append(p)
        else:
            percentiles.append(100-p)
    label = '_'.join(['senlen'] + [str(x) for x in pars[1:]])
    return (label, list(zip(percentiles, target)))
