from nltk.corpus import stopwords

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def Levenshtein(data_file, removestopwords=False):
    print('Levenshtein:')
    print('\tRemove stopwords:', removestopwords)

    distance = []
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
            d = levenshtein(line[1], line[2])
            distance.append(d)
            target.append(line[0])
    print()
    return list(zip(distance, target))