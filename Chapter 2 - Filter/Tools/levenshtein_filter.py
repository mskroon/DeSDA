input_file = '../Data/en-nl.raw'
output_file = '../Output/en-nl.raw.filtered'
removestopwords = True
stopwords = ['AUX', 'CCONJ', 'NUM']
transposition = True
threshold = 7



def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1
    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition
    return d[lenstr1 - 1, lenstr2 - 1]




if removestopwords:
    if stopwords is None:
        stopwords = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
with open(input_file, 'r') as input_file, open(output_file, 'w') as output_file:
    for line in input_file:
        line_copy = line
        line = line[:-1].split('\t')
        if removestopwords:
            line[0] = [w.split('|')[1] for w in line[0].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
            line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1] not in stopwords + ['PUNCT']]
        else:
            line[0] = [w.split('|')[1] for w in line[0].split() if w.split('|')[1]!='PUNCT']
            line[1] = [w.split('|')[1] for w in line[1].split() if w.split('|')[1]!='PUNCT']
        if not transposition:
            d = levenshtein(line[0], line[1])
        else:
            d = damerau_levenshtein_distance(line[0], line[1])
        if d <= threshold:
            output_file.write(line_copy)
