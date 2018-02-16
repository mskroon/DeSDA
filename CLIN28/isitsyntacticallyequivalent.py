# import easygui
import tkinter
import sys

# python3 isitsyntacticallyequivalent.py en-nl.pos.join.ud en-nl.syn.train
# en-nl.pos.join.ud not included due to size
# 	it consists of two columns: English and Dutch sentences, divided by a tab (\t)
#	columns contain sentence with all words POS-tagged with UD-tags, separated by a pipe (|):
#		e.g.: word|POS word|pos ...\tword|POS word|POS

corpus = set()
result = set()
YN = {}

inputfile = open(sys.argv[1], 'r')
for line in inputfile:
    line = tuple(line[:-1].split('\t'))
    if line != '' and (len(line[0].split()) <= 20 or len(line[1].split()) <= 20):
        corpus.add(line)
inputfile.close()

try:
    resultfile = open(sys.argv[2], 'r')
    for line in resultfile:
        line = line[:-1].split('\t')
        YN[line[0]] = YN.get(line[0], 0) + 1
        line = tuple(line[1:])
        if line != '':
            result.add(line)
    resultfile.close()
except FileNotFoundError:
    pass
resultfile = open(sys.argv[2], 'a')

corpus -= result

print(len(corpus))
# for S in corpus:
#     msg = ' '.join([w.split('|')[0] for w in S[0].split()]) + '\n\n' + ' '.join([w.split('|')[0] for w in S[1].split()])
#     title = 'Syntactically equivalent?'
#     choices = ['Yes', 'No', 'Quit']
#     reply = easygui.buttonbox(msg, title=title, choices=choices)
#     if reply == 'Yes':
#         resultfile.write('Y\t' + S[0] + '\t' + S[1] + '\n')
#     elif reply == 'No':
#         resultfile.write('N\t' + S[0] + '\t' + S[1] + '\n')
#     elif reply == 'Quit':
#         resultfile.close()
#         quit()

for S in corpus:
    print('Y: ' + str(YN.get('Y', 0)) + '\tN: ' + str(YN.get('N', 0)) + '\tTotal: ' + str(YN.get('Y', 0) + YN.get('N', 0)), end='\r')
    top = tkinter.Tk()
    def yes():
        resultfile.write('Y\t' + S[0] + '\t' + S[1] + '\n')
        YN['Y'] = YN.get('Y', 0) + 1
        top.destroy()
    def no():
        resultfile.write('N\t' + S[0] + '\t' + S[1] + '\n')
        YN['N'] = YN.get('N', 0) + 1
        top.destroy()
    def Q():
        print('Y: ' + str(YN.get('Y', 0)) + '\tN: ' + str(YN.get('N', 0)))
        top.destroy()
        resultfile.close()
        quit()
    def skip():
        top.destroy()
    msg = ' '.join([w.split('|')[0] for w in S[0].split()]) + '\n\n' + ' '.join([w.split('|')[0] for w in S[1].split()])
    tkinter.Label(top, text=msg, wraplength=512, font=("Helvetica", 16)).pack()
    tkinter.Button(top, text="Yes", command=yes, font=("Helvetica", 16)).pack()
    tkinter.Button(top, text="No", command=no, font=("Helvetica", 16)).pack()
    tkinter.Button(top, text="Skip", command=skip, font=("Helvetica", 16)).pack()
    tkinter.Button(top, text="Quit", command=Q, font=("Helvetica", 16)).pack()
    top.mainloop()
