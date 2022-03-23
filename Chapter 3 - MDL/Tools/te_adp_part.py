import re

inp = '../Data/conllu/conllu.nl'
outp = '../Data/conllu/conllu.te.nl'
inp = open(inp, 'r').read()
outp = open(outp, 'w')

P = re.compile('([Tt]e\t)ADP(.*\n.*[VERB|AUX])')

result = re.sub(P, r'\1PART\2', inp)
outp.write(result)
