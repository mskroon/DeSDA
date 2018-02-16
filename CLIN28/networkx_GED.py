import networkx as nx
from ufal.udpipe import *
from conllu.parser import parse
from collections import OrderedDict, Counter
from nltk.corpus import stopwords
from math import log
error = ProcessingError()

def calculate_idfs(data_file, p1, p2, MAN=False):
    print('\tCalculating idf values...')
    model1_idf = {}
    model2_idf = {}
    nr_sentences = 0
    with open(data_file, 'r') as file:
        for line in file:
            nr_sentences += 1
            line = line[:-1].split('\t')
            line[1] = [w.split('|')[0] for w in line[1].split()]
            line[2] = [w.split('|')[0] for w in line[2].split()]
            line[1] = parse(p1.process(' '.join(line[1]), error))
            line[2] = parse(p2.process(' '.join(line[2]), error))
            line[1] = [j for i in line[1] for j in i]
            line[2] = [j for i in line[2] for j in i]
            line[1] = [deep_convert_dict(od) for od in line[1]]
            line[2] = [deep_convert_dict(od) for od in line[2]]
            morph1 = set()
            morph2 = set()
            if MAN:
                for w in line[1]:
                    if w['feats'] is not None:
                        feats = {str(k)+'='+str(v) for k, v in w['feats'].items()}
                        morph1 |= feats
                for w in line[2]:
                    if w['feats'] is not None:
                        feats = {str(k)+'='+str(v) for k, v in w['feats'].items()}
                        morph2 |= feats
            line[1] = {w['lemma'] for w in line[1]} | morph1
            line[2] = {w['lemma'] for w in line[2]} | morph2
            for w in line[1]:
                model1_idf[w] = model1_idf.get(w, 0) + 1
            for w in line[2]:
                model2_idf[w] = model2_idf.get(w, 0) + 1
        for w, count in model1_idf.items():
            model1_idf[w] = log(nr_sentences / count)
        for w, count in model2_idf.items():
            model2_idf[w] = log(nr_sentences / count)
    print('\tCalculating idf values done.')
    return model1_idf, model2_idf

def tfidfs(c, idf, MAN=False):
    res = []
    for i, s in enumerate(c):
        morph = []
        if MAN:
            for w in s:
                if w['feats'] is not None:
                    feats = [str(k) + '=' + str(v) for k, v in w['feats'].items()]
                    morph += feats
        s = [w['lemma'] for w in s] + morph
        # s = s.split()
        # print(s)
        tf = Counter(s)
        res.append({})
        for j, w in enumerate(s):
            res[i][w] = tf[w]*idf[i][w] #raw frequency
            # res[i][w] = tf[w]*idf[i][w]/len(s) #term frequency adjusted for document length
            # res[i][w] = (.5 + .5 * tf[w]/tf.most_common()[0][1])*idf[i][w] #augmented frequency
            res[i][w] = (1 + log(tf[w])) * idf[i][w]
    return res


def my_node_subst_cost(n1, n2):
    n1 = set(n1.items())
    n2 = set(n2.items())
    d = n1 ^ n2
    d = {f[0] for f in d if f[0] != 'lemma'}
    # print(d)
    return len(d)

def my_edge_subst_cost(e1, e2):
    # print(e1, e2)
    if e1.get('deprel') == e2.get('deprel'):
        return 0
    else:
        return 1

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

def conllu_to_nx_graph(c, ignore_morphology=False, sw=None, morphology_as_nodes=False):
    c = {d['id']: d for d in c if d['id'] is not None}
    G = nx.MultiDiGraph()
    for id, w in c.items():
        if sw != []:
            if w['lemma'] in sw and w['deprel'] != 'root':
                continue
        features = {'upostag': w['upostag'], 'lemma': w['lemma']}
        if not ignore_morphology:
            if w['feats'] is not None:
                if morphology_as_nodes:
                    e = []
                    n = []
                    for feat, val in w['feats'].items():
                        e.append((id, val, {'deprel': feat.lower()}))
                        # e.append((id, val, {'deprel': feat}))
                        n.append((val, {'upostag': val, 'lemma': str(feat)+'='+str(val)}))
                        # n.append((val, {'upostag': 'MORPH', 'lemma': str(feat)+'='+str(val)}))
                    G.add_edges_from(e)
                    G.add_nodes_from(n)
                else:
                    features.update(w['feats'])
        G.add_nodes_from([(id, features)])
        if not w['head'] in [0, None]:
            # print((w['head'], id, {'deprel': w['deprel']}))
            # G.add_edges_from([(w['head'], id, {'deprel': w['deprel'].split(':')[0]})])
            add_edge(c, w, id, G, sw)
        # elif w['head'] == 0:
        #     G.add_nodes_from([(0, {})])
        #     G.add_edges_from([(0, id, {})])
    return G
    # print(c)

def Networkx_GED(data_file, M1, M2, ignore_morphology=False, removestopwords=False, morphology_as_nodes=False, tfidf=False):
    print('Networkx GED:')
    print('\tIgnore morphology:', ignore_morphology),
    print('\tRemove stopwords:', removestopwords),
    print('\tMorphology as nodes:', morphology_as_nodes),
    print('\ttf-idf:', tfidf),

    if ignore_morphology and morphology_as_nodes:
        print('Ignore morphology and morphology as nodes incompatible.')
        quit()
    M1 = Model.load(M1)
    M2 = Model.load(M2)
    pipeline_1 = Pipeline(M1, 'horizontal', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    pipeline_2 = Pipeline(M2, 'horizontal', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    if removestopwords:
        StopWords = [stopwords.words('english'), stopwords.words('dutch')]
    else:
        StopWords = [[], []]
    if tfidf:
        idf = calculate_idfs(data_file, pipeline_1, pipeline_2, morphology_as_nodes)
        # print(idf[0])
        # print(idf[1])
    value = []
    target = []
    with open(data_file, 'r') as DATA:
        for line in DATA:
            line = line[:-1].split('\t')
            line[1] = ' '.join([w.split('|')[0] for w in line[1].split()])
            line[2] = ' '.join([w.split('|')[0] for w in line[2].split()])
            # print(line)
            c = line[1:]

            c1 = max(parse(pipeline_1.process(c[0], error)), key=len)
            c2 = max(parse(pipeline_2.process(c[1], error)), key=len)
            c = ([deep_convert_dict(od) for od in c1], [deep_convert_dict(od) for od in c2])
            if tfidf:
                TfIdf = tfidfs(c, idf, morphology_as_nodes)
                # print(TfIdf)
            c = tuple(conllu_to_nx_graph(x, ignore_morphology=ignore_morphology, sw=StopWords[i], morphology_as_nodes=morphology_as_nodes) for i, x in enumerate(c))
            # print(line)
            # print(c[0].nodes, c[0].edges, c[1].nodes, c[1].edges)
            # print([c[0].nodes[n]['lemma'] for n in c[0].nodes])
            if tfidf:
                def my_node_del_cost(n1):
                    # if n1['upostag'] == 'MORPH':
                    #     return 1
                    return TfIdf[0][n1['lemma']]
                def my_node_ins_cost(n2):
                    # if n2['upostag'] == 'MORPH':
                    #     return 1
                    return TfIdf[1][n2['lemma']]
                def my_node_subst_cost_tfidf(n1, n2):
                    constant = (TfIdf[0][n1['lemma']]+TfIdf[1][n2['lemma']])/2
                    return my_node_subst_cost(n1, n2)*constant
                # print(c[0])
                d = nx.similarity.graph_edit_distance(c[0], c[1], node_subst_cost=my_node_subst_cost_tfidf,
                                                      edge_subst_cost=my_edge_subst_cost,
                                                      node_del_cost=my_node_del_cost,
                                                      node_ins_cost=my_node_ins_cost
                                                      )
            else:
                d = nx.similarity.graph_edit_distance(c[0], c[1], node_subst_cost=my_node_subst_cost,
                                                      edge_subst_cost=my_edge_subst_cost)
            value.append(d)
            target.append(line[0])
    print()
    return list(zip(value, target))

def add_edge(C, w, id, G, sw=[]):
    # print(d)
    if w['head'] == 0:
        pass
    elif C[w['head']]['deprel'] == 'root' or not C[w['head']]['lemma'] in sw:
        G.add_edges_from([(w['head'], id, {'deprel': C[id]['deprel'].split(':')[0]})])
    else:
        add_edge(C, C[w['head']], id, G, sw)
