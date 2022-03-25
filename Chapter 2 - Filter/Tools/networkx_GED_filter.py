import networkx as nx
from ufal.udpipe import *
from conllu import parse
from collections import OrderedDict
error = ProcessingError()

input_file = '../Data/de-en.raw'
M1 = '../Data/UDPipe_models/german-ud-2.0-conll17-170315.udpipe' #a UDPipe model
M2 = '../Data/UDPipe_models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
output_file = '../Output/en-nl.raw.filtered'
removestopwords = False
stopwords = []
threshold = 4



def my_node_subst_cost(n1, n2):
    if n1.get('upos') == n2.get('upos'):
        return 0
    else:
        return 1

def my_edge_subst_cost(e1, e2):
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

def remove_function_words(G, closed_set={'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'}):
    to_remove = set()
    for n in G.nodes:
        if nx.ancestors(G, n) == set():
            continue
        if G.nodes[n]['upos'] in closed_set:
            if nx.descendants(G, n) == set():
                to_remove.add(n)
            else:
                parent = list(G.predecessors(n))[0]
                for child in G[n]:
                    G.add_edges_from([(parent, child, G.edges[(n,child)])])
                to_remove.add(n)
    G.remove_nodes_from(to_remove)

def conllu_to_nx_graph(C, pos_to_ignore):
    G = nx.DiGraph()
    for w in C:
        if w['upostag'] == 'PUNCT':
            continue
        G.add_node(w['id'], upos=w['upostag'])
        if not w['head'] == 0:
            G.add_node(w['head'], upos=C[w['head'] - 1]['upostag'])
        G.add_edge(w['head'], w['id'], deprel=w['deprel'].split(':')[0])
    remove_function_words(G, closed_set=pos_to_ignore)
    return G


def is_generator_empty(g):
    try:
        first = next(g)
        return False
    except StopIteration:
        return True


M1 = Model.load(M1)
M2 = Model.load(M2)
pipeline_1 = Pipeline(M1, 'horizontal', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
pipeline_2 = Pipeline(M2, 'horizontal', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
if removestopwords:
    if stopwords is None:
        stopwords = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
else:
    stopwords = []
with open(input_file, 'r') as input_file, open(output_file, 'w') as output_file:
    for line in input_file:
        line_copy = line
        line = line[:-1].split('\t')
        line[0] = ' '.join([w.split('|')[0] for w in line[0].split()])
        line[1] = ' '.join([w.split('|')[0] for w in line[1].split()])
        c = line

        c1 = max(parse(pipeline_1.process(c[0], error)), key=len)
        c2 = max(parse(pipeline_2.process(c[1], error)), key=len)
        c = ([deep_convert_dict(od) for od in c1], [deep_convert_dict(od) for od in c2])
        c = tuple(conllu_to_nx_graph(x, pos_to_ignore=stopwords) for x in c)
        d = nx.similarity.optimize_graph_edit_distance(c[0], c[1], node_subst_cost=my_node_subst_cost,
                                              edge_subst_cost=my_edge_subst_cost, upper_bound=threshold)
        if not is_generator_empty(d):
            output_file.write(line_copy)

