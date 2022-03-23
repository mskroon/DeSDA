import sys
result = sys.argv[1]
out = result + '.trans'
lab = sys.argv[2]

ids = {i: w.strip('\n') for i, w in enumerate(open(lab, 'r'))}

with open(out, 'w') as wf:
    for line in open(result, 'r'):
        line = line.split(' ')
        value = line[-3:]
        line = line[:-4]
        line = [ids[int(i)] for i in line]
        wf.write(' '.join(line + value))