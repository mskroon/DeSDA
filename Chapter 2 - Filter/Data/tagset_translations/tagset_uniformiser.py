import sys

tag_dict = {}
with open(sys.argv[2], 'r') as tags:
    for line in tags:
        line = line[:-1].split('\t')
        tag_dict[line[0]] = line[1]

with open(sys.argv[1], 'r') as Input, open(sys.argv[3], 'w') as Output:
    for line in Input:
        line = line[:-1].split()
        for i, w in enumerate(line):
            w = w.split('|')
            w[1] = tag_dict.get(w[1], w[1])
            w = '|'.join(w)
            line[i] = w
        line = ' '.join(line)
        Output.write(line + '\n')
