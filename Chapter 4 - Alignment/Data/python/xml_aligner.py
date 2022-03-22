import xmltodict, os
Bibles_XML_location = '../XML_Bibles'

'''
A tool to align the xml Bible as provided by
    Christodouloupoulos, C. and Steedman, M. (2015). 'A massively parallel corpus: The Bible in 100 languages'.
        In: Language resources and evaluation 49.2, pp. 375--395.
such that the output contains only the verses present in both translations.

Change Bibles_XML_location above to appropriate path.
'''

def recursive_items(d):
    for k, v in d.items():
        if type(v) is xmltodict.OrderedDict:
            yield (k, v)
            yield from recursive_items(v)
        elif type(v) is list:
            for i in v:
                if type(i) is xmltodict.OrderedDict:
                    yield (k, i)
                    yield from recursive_items(i)
        else:
            continue

D = {}
for file in os.listdir(Bibles_XML_location):
    if file.endswith('.xml'):
        print(file)
        s = {}
        with open(Bibles_XML_location + file, 'r', encoding='utf8') as xml:
            B = xmltodict.parse(xml.read())
            for book in B['cesDoc']['text']['body']['div']:
                for k, v in recursive_items(book):
                    try:
                        if v['@type'] == 'verse':
                            # print(v['@id'])
                            s[v['@id']] = v['#text']
                    except KeyError:
                        continue
        D[file] = s

verses_in_all_versions = set.intersection(*[set(v.keys()) for v in D.values()])
print(len(verses_in_all_versions))

list(verses_in_all_versions)
for L in D.keys():
    L_file = open(L + '.align', 'w', encoding='utf8')
    for verse in verses_in_all_versions:
        L_file.write(verse + '\t' + D[L][verse] + '\n')

