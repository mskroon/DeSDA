import networkx as nx
from conllu import parse_incr


languages = list(sorted(['en', 'te.nl']))
threshold = 4
pos_to_ignore={'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'}


data1 = '../Data/conllu/conllu.' + languages[0]
data2 = '../Data/conllu/conllu.' + languages[1]
Lpair = '-'.join([l.split('.')[-1] for l in languages])
output1 = '../Data/conllu/' + Lpair + '/conllu.filter.' + languages[0]
output2 = '../Data/conllu/' + Lpair + '/conllu.filter.' + languages[1]
output1 = open(output1, 'w')
output2 = open(output2, 'w')

A_B_parallel = zip(parse_incr(open(data1, 'r')), parse_incr(open(data2, 'r')))


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

def conllu_to_nx_graph(C):
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

for A, B in A_B_parallel:
    a = conllu_to_nx_graph(A)
    b = conllu_to_nx_graph(B)
    d = nx.similarity.optimize_graph_edit_distance(a, b, node_subst_cost=my_node_subst_cost,
                                          edge_subst_cost=my_edge_subst_cost, upper_bound=threshold)
    d = list(d)
    if d != []:
        output1.write(A.serialize())
        output2.write(B.serialize())
