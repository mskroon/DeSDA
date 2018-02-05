from ufal.udpipe import *
from conllu.parser import parse
from collections import OrderedDict
from nltk.corpus import stopwords
import zss
error = ProcessingError()


def deep_convert_dict(layer):
    to_ret = layer
    if isinstance(layer, OrderedDict):
        to_ret = dict(layer)
    try:
        for key, value in to_ret.items():
            to_ret[key] = deep_convert_dict(value)
    except AttributeError:
        pass

    return to_ret

def UD_zss(c, pipeline_1, pipeline_2, ignore_morphology=False, sw=[[], []]):
    c1 = max(parse(pipeline_1.process(c[0], error)), key=len)
    c2 = max(parse(pipeline_2.process(c[1], error)), key=len)
    c = ([deep_convert_dict(od) for od in c1], [deep_convert_dict(od) for od in c2])
    c = list(c)
    for i, C in enumerate(c):
        C = {d['id'] : d for d in C if d['id'] is not None}
        # print(C)
        root = None
        edges = {}
        nodes = {}
        for d in C.values():
            if sw != [[], []]:
                if d['lemma'] in sw[i] and d['deprel'] != 'root':
                    # print(d['id'], d['lemma'], d['deprel'])
                    continue
            if d['id'] is None:
                continue
            if d['deprel'] == 'root':
                root = d['id']
            else:
                # if d['head'] not in edges:
                #     edges[d['head']] = set()
                # edges[d['head']].add(d['id'])
                add_edge(C, d, d['id'], edges, sw[i])
            if not (d['feats'] is None or ignore_morphology):
                for fk, fv in d['feats'].items():
                    f = fk + '=' + fv
                    if d['id'] not in edges:
                        edges[d['id']] = set()
                    edges[d['id']].add(f)
                    nodes[f] = zss.Node(f)
            nodes[d['id']] = zss.Node('upostag=' + d['upostag'] + ' deprel=' + d['deprel'].split(':')[0])
        # print(edges)
        for ek, ev in edges.items():
            for e in ev:
                # nodes[ek]
                # nodes[e]
                nodes[ek].addkid(nodes[e])
        c[i] = nodes[root]
    zs = zss.simple_distance(c[0], c[1])

    # print(zs, c[0], c[1])
    return zs

def Zhang_Shasha_UD(data_file, M1, M2, ignore_morphology=False, removestopwords=False):
    print('Zhang-Shasha:')
    print('\tIgnore morphology:', ignore_morphology)
    print('\tRemove stopwords:', removestopwords)

    M1 = Model.load(M1)
    M2 = Model.load(M2)
    pipeline_1 = Pipeline(M1, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    pipeline_2 = Pipeline(M2, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    if removestopwords:
        model1stopwords = stopwords.words('english')
        model2stopwords = stopwords.words('dutch')
    else:
        model1stopwords = []
        model2stopwords = []
    value = []
    target = []
    with open(data_file, 'r') as DATA:
        for line in DATA:
            line = line[:-1].split('\t')
            line[1] = ' '.join([w.split('|')[0] for w in line[1].split()])
            line[2] = ' '.join([w.split('|')[0] for w in line[2].split()])
            d = UD_zss(line[1:], pipeline_1, pipeline_2, ignore_morphology, sw=[model1stopwords, model2stopwords])
            value.append(d)
            target.append(line[0])
    print()
    return list(zip(value, target))

def add_edge(C, d, id, edges, sw=[]):
    # print(d)
    if d['head'] == 0:
        pass
        # if 0 not in edges:
        #     edges[0] = set()
        # edges[0].add(id)
    elif C[d['head']]['deprel'] == 'root' or not C[d['head']]['lemma'] in sw:
        if d['head'] not in edges:
            edges[d['head']] = set()
        edges[d['head']].add(id)
    else:
        add_edge(C, C[d['head']], id, edges, sw)