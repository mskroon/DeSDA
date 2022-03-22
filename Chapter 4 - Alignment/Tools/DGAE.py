__author__ = 'marti'
from collections import defaultdict
from simple_tokenizer import tokenize_text
import ufal.udpipe
import networkx as nx
from itertools import combinations, combinations_with_replacement
import copy
import time
import multiprocessing
import pandas as pd
from functools import partial
import sys

n_processes = multiprocessing.cpu_count() - 1

class Model:
    def __init__(self, path):
        """Load given model."""
        self.model = ufal.udpipe.Model.load(path)
        if not self.model:
            raise Exception("Cannot load UDPipe model from file '%s'" % path)

    def tokenize(self, text):
        """Tokenize the text and return list of ufal.udpipe.Sentence-s."""
        tokenizer = self.model.newTokenizer(self.model.DEFAULT)
        if not tokenizer:
            raise Exception("The model does not have a tokenizer")
        return self._read(text, tokenizer)

    def read(self, text, format):
        """Load text in the given format (conllu|horizontal|vertical) and return list of ufal.udpipe.Sentence-s."""
        input_format = ufal.udpipe.InputFormat.newInputFormat(format)
        if not input_format:
            raise Exception("Cannot create input format '%s'" % format)
        return self._read(text, input_format)

    def _read(self, text, input_format):
        input_format.setText(text)
        error = ufal.udpipe.ProcessingError()
        sentences = []

        sentence = ufal.udpipe.Sentence()
        while input_format.nextSentence(sentence, error):
            sentences.append(sentence)
            sentence = ufal.udpipe.Sentence()
        if error.occurred():
            raise Exception(error.message)

        return sentences

    def read_list(self, text, format):
        result = []
        for sentence in text:
            result += self.read(sentence, format)
        return result

    def tag(self, sentence):
        """Tag the given ufal.udpipe.Sentence (inplace)."""
        self.model.tag(sentence, self.model.DEFAULT)

    def parse(self, sentence):
        """Parse the given ufal.udpipe.Sentence (inplace)."""
        self.model.parse(sentence, self.model.DEFAULT)

    def write(self, sentences, format):
        """Write given ufal.udpipe.Sentence-s in the required format (conllu|horizontal|vertical)."""

        output_format = ufal.udpipe.OutputFormat.newOutputFormat(format)
        output = ''
        for sentence in sentences:
            output += output_format.writeSentence(sentence)
        output += output_format.finishDocument()

        return output

    def make_nx_graph(self, sentences, nested_feats = True):
        G = nx.DiGraph()
        for i, sentence in enumerate(sentences):
            for word in sentence.words:
                if word.id < 1:
                    continue
                id = word.id
                if id not in G:
                    G.add_node(id)
                G.nodes[id]['form'] = word.form
                G.nodes[id]['lemma'] = word.lemma
                G.nodes[id]['misc'] = word.misc
                G.nodes[id]['pos'] = word.upostag
                G.add_edge(word.head, id)
                G.nodes[id]['deprel'] = word.deprel
                G.nodes[id]['deps'] = word.deps
                if word.feats == '':
                    feats = {}
                else:
                    feats = word.feats.split('|')
                    feats = [feat.split('=') for feat in feats]
                    feats = {k: v for k, v in feats}
                if nested_feats:
                    G.nodes[id]['feats'] = feats
                else:
                    G.nodes[id].update(feats)
                G.nodes[id]['label'] = '\n'.join([': '.join((k, str(v))) for k, v in G.nodes[id].items() if v not in ['', {}]])
                G.nodes[id]['label'] = 'id: ' + str(word.id - 1) + '\n' + G.nodes[id]['label']
        return G

    def tag_words(self, sentences):
        output = []
        for sentence in sentences:
            sen_output = []
            for word in sentence.words:
                sen_output.append('_'.join((word.form, word.upostag)))
            output.append(sen_output[1:])
        return output


def get_tree_path(G, source, target):
    try:
        path = nx.shortest_path(G, source, target)
        path = sorted(enumerate(path), key=lambda t:t[1])
        path = [G.nodes[n]['deprel']+str(i) for i, n in path]
    except nx.exception.NetworkXNoPath:
        try:
            path = nx.shortest_path(G, target, source)
            path = sorted(enumerate(path), key=lambda t:t[1])
            path = [G.nodes[n]['deprel']+str(i+1-len(path)) for i, n in path]
        except nx.exception.NetworkXNoPath:
            lca = nx.lowest_common_ancestor(G, source, target)
            path_up = nx.shortest_path(G, lca, source)
            path_down = nx.shortest_path(G, lca, target)
            path_up = [(G.nodes[n]['deprel']+str(i+1-len(path_up)), n) for i, n in enumerate(path_up)]
            path_down = [(G.nodes[n]['deprel']+str(i+1)+'*', n) for i, n in enumerate(path_down[1:])]
            path = sorted(path_up+path_down, key=lambda t:t[1])
            path = [deprel for deprel, i in path]
    return path


def _read_data(data, nested_feats=True, include_children=False, include_parents=False, include_no_cross=False, include_cross_source=False):
        src_sentence, trg_sentence, src_alignment, trg_alignment = data
        _, src_sentence = src_sentence.split('\t', 1)
        _, trg_sentence = trg_sentence.split('\t', 1)
        src_sentence = tokenize_text(src_sentence)
        trg_sentence = tokenize_text(trg_sentence)
        model = copy.copy(main_model)
        src_sentence_graph = model.read_list([' '.join(src_sentence)], 'horizontal')[0]
        model.tag(src_sentence_graph)
        model.parse(src_sentence_graph)
        src_sentence_graph = model.make_nx_graph([src_sentence_graph], nested_feats=nested_feats)
        src_alignment = {tuple(int(x) for x in t.split('-')) for t in src_alignment.strip('\n').split(' ')}
        trg_alignment = {tuple(int(x) for x in t.split('-')) for t in trg_alignment.strip('\n').split(' ')}
        alignments = src_alignment | trg_alignment
        temp_src_dict = defaultdict(set)
        temp_trg_dict = defaultdict(set)
        for x, y in alignments:
            temp_src_dict[x].add(y)
            temp_trg_dict[y].add(x)
        for node in src_sentence_graph.nodes:
            if node == 0:
                continue
            del src_sentence_graph.nodes[node]['label']
            if nested_feats:
                src_sentence_graph.nodes[node]['feats'] = frozenset(src_sentence_graph.nodes[node]['feats'].items())
                if src_sentence_graph.nodes[node]['pos'] == 'VERB':
                    child_relations = [src_sentence_graph.nodes[child]['deprel'] for child in src_sentence_graph.neighbors(node)]
                    if 'obj' in child_relations or 'nsubj:pass' in child_relations or 'aux:pass' in child_relations:
                        src_sentence_graph.nodes[node]['pos'] += ':Trans'
                    else:
                        src_sentence_graph.nodes[node]['pos'] += ':Intrans'
                if src_sentence_graph.nodes[node]['deprel'] == 'conj':
                    mother = list(src_sentence_graph.predecessors(node))[0]
                    src_sentence_graph.nodes[node]['deprel'] = src_sentence_graph.nodes[mother]['deprel'] + ':conj'
            src_sentence_graph.nodes[node]['translation'] = tuple(trg_sentence[j] for j in sorted(temp_src_dict[node-1]))
            src_sentence_graph.nodes[node]['cross'] = []
            if include_no_cross:
                src_sentence_graph.nodes[node]['no_cross'] = []
        for alignment_a, alignment_b in combinations(alignments, 2):
            i, j = alignment_a
            p, q = alignment_b
            if i == p or j == q:
                continue
            if src_sentence_graph.nodes[i+1]['pos'] == 'PUNCT' or src_sentence_graph.nodes[p+1]['pos'] == 'PUNCT':
                continue
            if (i > p and j < q) or (i < p and j > q):
                src_sentence_graph.nodes[i+1]['cross'].append(p+1)
                src_sentence_graph.nodes[p+1]['cross'].append(i+1)
            elif include_no_cross:
                src_sentence_graph.nodes[i+1]['no_cross'].append(p+1)
                src_sentence_graph.nodes[p+1]['no_cross'].append(i+1)
        for node in src_sentence_graph.nodes:
            if node == 0:
                continue
            if src_sentence_graph.nodes[node]['translation'] == tuple():
                src_sentence_graph.nodes[node]['ancestor_cross'] = tuple(tuple(),)
                src_sentence_graph.nodes[node]['descendant_cross'] = tuple(tuple(),)
                src_sentence_graph.nodes[node]['cousin_cross'] = tuple(tuple(),)
                del src_sentence_graph.nodes[node]['cross']
                if include_no_cross:
                    src_sentence_graph.nodes[node]['no_cross'] = tuple()
                continue
            crossings = src_sentence_graph.nodes[node]['cross']
            descendant_crossings = [c for c in crossings if c in nx.descendants(src_sentence_graph, node)]
            descendant_crossings = [c for c in descendant_crossings if not any(other_c in src_sentence_graph.predecessors(c) for other_c in descendant_crossings)]
            ancestor_crossings = [c for c in crossings if c in nx.ancestors(src_sentence_graph, node)]
            ancestor_crossings = [c for c in ancestor_crossings if not any(other_c in src_sentence_graph.successors(c) for other_c in ancestor_crossings)]
            cousin_crossings = [c for c in crossings if c not in set(nx.descendants(src_sentence_graph, node)) | set(nx.ancestors(src_sentence_graph, node))]
            cousin_crossings = [c for c in cousin_crossings if not any(other_c in src_sentence_graph.predecessors(c) for other_c in cousin_crossings)]
            src_sentence_graph.nodes[node]['ancestor_cross'] = tuple(ancestor_crossings)
            src_sentence_graph.nodes[node]['descendant_cross'] = tuple(descendant_crossings)
            src_sentence_graph.nodes[node]['cousin_cross'] = tuple(cousin_crossings)
            del src_sentence_graph.nodes[node]['cross']
            for method in ['ancestor_cross', 'descendant_cross', 'cousin_cross'] + ['no_cross' for _ in range(1) if include_no_cross]:
                crossings = src_sentence_graph.nodes[node][method]
                paths = []
                for c in crossings:
                    try:
                        path = nx.shortest_path(src_sentence_graph, node, c)
                        path = sorted(enumerate(path), key=lambda t:t[1])
                        path = [src_sentence_graph.nodes[n]['deprel']+str(i) for i, n in path]
                        paths.append(tuple(path))
                    except nx.exception.NetworkXNoPath:
                        # pass
                        try:
                            path = nx.shortest_path(src_sentence_graph, c, node)
                            path = sorted(enumerate(path), key=lambda t:t[1])
                            path = [src_sentence_graph.nodes[n]['deprel']+str(i+1-len(path)) for i, n in path]
                            paths.append(tuple(path))
                        except nx.exception.NetworkXNoPath:
                            lca = nx.lowest_common_ancestor(src_sentence_graph, node, c)
                            path_up = nx.shortest_path(src_sentence_graph, lca, node)
                            path_down = nx.shortest_path(src_sentence_graph, lca, c)
                            path_up = [(src_sentence_graph.nodes[n]['deprel']+str(i+1-len(path_up)), n) for i, n in enumerate(path_up)]
                            path_down = [(src_sentence_graph.nodes[n]['deprel']+str(i+1)+'*', n) for i, n in enumerate(path_down[1:])]
                            path = sorted(path_up+path_down, key=lambda t:t[1])
                            path = [deprel for deprel, i in path]
                            paths.append(tuple(path))
                crossings = paths
                for p_i, path in enumerate(crossings):
                    if include_cross_source:
                        path = tuple(path)
                    else:
                        path = tuple([n if n[-1]!='0' else '_' for n in path])
                    crossings[p_i] = path
                if crossings == [] and src_sentence_graph.nodes[node].get('translation', tuple()) != tuple() and method != 'no_cross':
                    if include_cross_source:
                        crossings.append((src_sentence_graph.nodes[node]['deprel'] + '0',))
                    else:
                        crossings.append(('_',))
                src_sentence_graph.nodes[node][method] = tuple(crossings)
        if include_children or include_parents:
            for node in src_sentence_graph.nodes:
                if node == 0:
                    continue
                if include_children:
                    children = src_sentence_graph.neighbors(node)
                    children = [child for child in children if src_sentence_graph.nodes[child]['pos'] not in ['INTJ', 'PUNCT']]
                    src_sentence_graph.nodes[node]['children'] = frozenset([src_sentence_graph.nodes[child]['lemma']+ '_' + src_sentence_graph.nodes[child].get('pos', 'None')+'_'+src_sentence_graph.nodes[child]['deprel'] if src_sentence_graph.nodes[child]['pos'] not in ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB', 'VERB:Trans', 'VERB:Intrans'] else src_sentence_graph.nodes[child]['pos']+'_'+src_sentence_graph.nodes[child]['deprel'] for child in children])
                if include_parents:
                    parent = list(src_sentence_graph.predecessors(node))[0]
                    if src_sentence_graph.nodes[parent].get('pos', None) not in ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB', 'VERB:Trans', 'VERB:Intrans', None]:
                        src_sentence_graph.nodes[node]['parents'] = src_sentence_graph.nodes[parent].get('lemma', 'None') + '_' + src_sentence_graph.nodes[parent].get('pos', 'None') + '_' + src_sentence_graph.nodes[parent].get('deprel', 'None')
                    else:
                        src_sentence_graph.nodes[node]['parents'] = src_sentence_graph.nodes[parent].get('pos', 'None') + '_' + src_sentence_graph.nodes[parent].get('deprel', 'None')
                    if parent < node:
                        src_sentence_graph.nodes[node]['parents'] = '<' + src_sentence_graph.nodes[node]['parents']
                    elif parent > node:
                        src_sentence_graph.nodes[node]['parents'] = src_sentence_graph.nodes[node]['parents'] + '>'
        result = []
        for i, w in enumerate(src_sentence):
            feature_bundle = src_sentence_graph.nodes[i+1]
            if feature_bundle.get('pos', '') == 'PUNCT':
                continue
            result.append(feature_bundle)
        return result


def is_iterable(x, ignore=str):
    try:
        iter(x)
        if not isinstance(x, ignore):
            return True
        else:
            return False
    except TypeError:
        return False


def read_data(src, trg, maximum=-1, path='Bible Corpus/', ext='.xml.align', nested_feats=True, include_children=False, include_parents=False, include_no_cross=False, include_cross_source=False):
    src_file = path + 'python/' + src + ext
    src_alignments = path + '-'.join([src, trg]) + '/' + '-'.join([src, trg]) + '.fwd'
    trg_file = path + 'python/' + trg + ext
    trg_alignments = path + '-'.join([src, trg]) + '/' + '-'.join([src, trg]) + '.rev'
    data = zip(open(src_file, 'r', encoding='utf8').readlines(), open(trg_file, 'r', encoding='utf8').readlines(), open(src_alignments, 'r', encoding='utf8').readlines(), open(trg_alignments, 'r', encoding='utf8').readlines())
    data = list(data)[:maximum]
    pool = multiprocessing.Pool(n_processes)
    kwargs = {'nested_feats': nested_feats, 'include_children': include_children, 'include_parents': include_parents, 'include_no_cross': include_no_cross, 'include_cross_source': include_cross_source}
    results = pool.map(partial(_read_data, **kwargs), data, n_processes)
    results = [x for y in results for x in y]
    pool.close()
    df = pd.DataFrame(results)
    for col_name in df.columns:
        if is_iterable(df[col_name].iloc[0]):
            T = type(df[col_name].iloc[0])
            df[col_name] = df[col_name].apply(lambda x: x if len(x)!=0 else T([None]))
    print("Reading done.")
    return df











def main(src, trg, maximum=-1, minimum_freq=-1, path='Bible Corpus/', ext='.xml.align', nested_feats=True, sorting_keys=('lemma', 'pos'), include_children=False, include_parents=False, include_cross_source=False):

    sub_start = time.time()
    print('Starting processing:', '-'.join([src, trg]), ', sorting on', sorting_keys)
    print('Reading...', end=' ')
    df = read_data(src=src, trg=trg, maximum=maximum, path=path, ext=ext, nested_feats=nested_feats, include_children=include_children, include_parents=include_parents,include_cross_source=include_cross_source)
    # print('Reading done. Took', time.time()-sub_start)

    with pd.option_context('display.max_rows', 20, 'display.max_columns', None):
        for grouped in sorted(df.groupby(list(sorting_keys)), key=lambda g: len(g[1])):
                name, group = grouped
                if len(group) < minimum_freq:
                    continue
                print(name, len(group))
                for col_name in group.columns:
                    if not is_iterable(group[col_name].iloc[0]):
                        count = group[col_name].value_counts().to_dict()
                        count = {k: v for k, v in count.items() if v >= minimum_freq}
                        print(col_name, '\t', sorted(count.items(), reverse=True, key=lambda t: t[1])[:20])
                    else:
                        temp_col = pd.Series(['|'.join(str(t) for t in s) for s in group[col_name]])
                        count = temp_col.str.split('|', expand=True).stack().value_counts().to_dict()
                        count = {k: v for k, v in count.items() if v >= minimum_freq}
                        print(col_name, '\t', sorted(count.items(), reverse=True, key=lambda t: t[1])[:20])
                value_counts = group.value_counts().loc[lambda x: x >= 2]
                if value_counts.shape[0] != 0:
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None, 'display.expand_frame_repr', False):
                        print()
                        print(value_counts.head(20).to_string())
                if value_counts.shape[0] > 20:
                    print('...')
                print()
                print()
    print("Processing took:", time.time() - sub_start)
    if write:
        f.close()





main_model = Model("english-partut-ud-2.5-191206.udpipe")
setup = (('en', 'hu'), ['pos', 'deprel'])
total_start = time.time()
write = True
data_location = '../Data/'
output_location = '../Output/'

if __name__ =="__main__":
    lang_pair, sorting_keys = setup
    sub_time = time.time()
    src, trg = lang_pair
    if write:
        f_name = output_location + "DGAE_" + src + '-' + trg + '_' + '_'.join(sorting_keys) + '.txt'
        f = open(f_name, 'w', encoding='utf8')
        sys.stdout = f
    main(src, trg, path=data_location, maximum=-1, minimum_freq=5, nested_feats=True, sorting_keys=sorting_keys, include_children=True, include_parents=True, include_cross_source=False)

