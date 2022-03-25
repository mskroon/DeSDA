from scipy.stats import percentileofscore

input_file = '../Data/en-nl.raw'
output_file = '../Output/en-nl.raw.filtered'
removestopwords = True
stopwords = ['AUX', 'NUM']
threshold = 20.625



def ratio(a, b):
    if b == 0:
        return 0
    return a/b


if removestopwords:
    if stopwords is None:
        stopwords = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
value = []
with open(input_file, 'r') as DATA:
    for line in DATA:
        line = line[:-1].split('\t')
        print(line)
        if removestopwords:
            line[0] = [w.split('|')[1] for w in line[0].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
            line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
        else:
            line[0] = [w.split('|')[1] for w in line[0].split() if w.split('|')[1]!='PUNCT']
            line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1]!='PUNCT']
        d = ratio(len(line[0]), len(line[1]))
        value.append(d)
percentiles = []
for v in value:
    p = percentileofscore(value, v)
    if p < 50:
        percentiles.append(p)
    else:
        percentiles.append(100-p)
with open(output_file, 'w') as out:
    for sentence_pair, percentile in zip(open(input_file, 'r'), percentiles):
        if percentile >= threshold:
            out.write(sentence_pair)


