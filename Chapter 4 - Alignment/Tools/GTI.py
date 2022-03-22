__author__ = 'marti'
import pandas as pd
from DGAE import read_data, is_iterable
import numpy as np
import sys
from collections import Counter

data = pd.DataFrame()

def intersect(L):
    res = L[0]
    for l in L[1:]:
        res &= l
    return res

def do_the_thing(grouped, depth=0, abs_min = 5, rel_min = 0.01):
    name, group = grouped
    if len(group) >= abs_min:
        nunique = group.apply(pd.Series.nunique)
        cols_to_drop = nunique[nunique == 1].index
        group = group.drop(cols_to_drop, axis=1)
        for col_name in group.columns:
            if type(group[col_name].iloc[0][1]) in [tuple, set, frozenset, list]:
                T = type(group[col_name].iloc[0][1])
                S = group[col_name].map(lambda x: set(x[1]))
                S = intersect(S.tolist())
                group[col_name] = group[col_name].apply(lambda x: (x[0], T([y for y in x[1] if y not in S])))
                group[col_name] = group[col_name].apply(lambda x: x if len(x[1]) != 0 else (x[0], T([None])))
        print('\t'*depth + str(name), '\tCount:', len(group))
        try:
            vc = group[[col_name for col_name in group.columns if col_name != 'id']].value_counts()
            vc = vc.rename(lambda x: x[1])
            if vc.shape[0] != 0:
                with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None, 'display.expand_frame_repr', False):
                    print('\t'*(depth+1) + 'Most frequent:')
                    print('\t'*(depth+1), vc.head(20).to_string().replace("\n", "\n"+'\t'*depth+'\t '))
            if vc.shape[0] > 20:
                print('\t'*(depth+1) + ' ...')
        except ValueError:
            pass
        Hs = {}
        if set(group.columns) != {'parents', 'id'}:
            print('\t'*(depth+1) + 'Value distributions:')
        for column in group.columns:
            if column != 'parents' and column != 'id':
                col_name = column
                column = group[column].value_counts()
                column = round(column / column.sum(), 5)
                print('\t'*(depth+1), col_name, '\t', {k[1]: v for k, v in column[:10].to_dict().items()})
                H = round((-np.log2(column) * column).sum(), 5)
                Hs[column.name] = H
                # print('\t', column.name, '\t', H)
        if set(group.columns) != {'parents', 'id'}:
            print('\t'*(depth+1) + 'Entropies:\t', Hs)
        lowest_H = min(Hs.items(), key=lambda item: item[1], default=(None, 0))
        if set(group.columns) != {'parents', 'id'}:
            print('\t'*(depth+1) + 'Lowest:\t\t', lowest_H[0])
        depth += 1
        if len(Hs) >= 2:
            if type(group[lowest_H[0]].iloc[0][1]) not in [tuple, set, frozenset, list]:
                for sub_grouped in sorted(group.groupby([lowest_H[0]]), key=lambda g: len(g[1]), reverse=True):
                    if len(sub_grouped[1]) < abs_min or len(sub_grouped[1]) < rel_min * len(group):
                        break
                    do_the_thing(sub_grouped, depth, abs_min=abs_min, rel_min=rel_min)
            else:
                g = group[lowest_H[0]]
                freqs = g.map(lambda x: Counter(x[1]))
                subgroups = {}
                for x, f in sorted(freqs.sum().items(), key=lambda x: x[1], reverse = True):
                    indexes = g.apply(lambda t: x in t[1])
                    indexes = indexes[indexes == True].index.tolist()
                    subgroups[(lowest_H[0], x)] = group.loc[indexes]
                for sub_grouped in subgroups.items():
                    if len(sub_grouped[1]) < abs_min or len(sub_grouped[1]) < rel_min * len(group):
                        break
                    do_the_thing(sub_grouped, depth, abs_min=abs_min, rel_min=rel_min)




setup = (('en', 'hu'), ['pos', 'deprel'])
write = True
data_location = '../Data/'
output_location = '../Output/'


if __name__ =="__main__":
    lang_pair, sorting_keys = setup
    src, trg = lang_pair
    if write:
        f_name = output_location + "GTI_" + src + '-' + trg + '_' + '_'.join(sorting_keys) + '.txt'
        f = open(f_name, 'w', encoding='utf8')
        sys.stdout = f
    df = read_data(src, trg, path=data_location, maximum=-1, nested_feats=True, include_children=True, include_parents=True)
    # print(df)
    def sort_if_frozenset(col):
        if isinstance(col.iloc[0], frozenset):
            return col.apply(lambda x: tuple(sorted(x)))
        else:
            return col
    df['id'] = range(len(df))
    df = df.apply(sort_if_frozenset)
    for col_name in df.columns:
        df[col_name] = df[col_name].apply(lambda x: (col_name, x))
    if sorting_keys == []:
        do_the_thing((None, df))
    else:
        for grouped in sorted(df.groupby(list(sorting_keys)), key=lambda g: len(g[1]), reverse=True):
            do_the_thing(grouped)
    if write:
        f.close()
    del df