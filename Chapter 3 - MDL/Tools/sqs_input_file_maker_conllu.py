from conllu import parse_incr
import sys
import itertools

inputfile = sys.argv[1]
filename = inputfile.split('/')[-1]
inputfile = open(inputfile, 'r', encoding='utf-8')

vocab = set()
lines = []

for s in parse_incr(inputfile):
    line = []
    for w in s:
        tag = w['upostag']
		line.append(tag)
    vocab |= set(line)
    lines.append(line)

vocab = {w: i for i, w in enumerate(vocab)}
lines = [[vocab[w] for w in s] for s in lines]
vocab = {v: k for k, v in vocab.items()}


outputfilelocation = sys.argv[2]
vocabfile = outputfilelocation + filename + '.lab'
with open(vocabfile, 'w') as f:
    i = 0
    while True:
        try:
            f.write(vocab[i] + '\n')
            i += 1
        except KeyError:
            break

datafile = outputfilelocation + filename + '.dat'
lines = [' '.join(map(str, line)) for line in lines]
data = ' -1 '.join(lines)
open(datafile, 'w').write(data)
