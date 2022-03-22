__author__ = 'marti'
import pandas as pd
from itertools import combinations, chain, dropwhile
from collections import Counter
from collections.abc import Iterable
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from scipy import sparse
import sparse as sparse_package
import warnings
from DGAE import read_data
import sys
warnings.filterwarnings("ignore")



def all_n_grams(W):
    result = []
    if isinstance(W, str):
        for n in range(1, len(W) + 1):
            for i in range(len(W) - n + 1):
                result.append(W[i:n+i])
    else:
        try:
            iter(W)
            for w in W:
                result += all_n_grams(w)
        except TypeError:
            raise TypeError
    return result


def flatten(items):
    """Yield items from any nested iterable; see REF."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def all_prefixes_and_suffixes(W):
    result = []
    if isinstance(W, str):
        result.append(W)
        for i in range(1, len(W)):
            result.append('-' + W[i:])
            result.append(W[:-i] + '-')
    else:
        try:
            iter(W)
            for w in W:
                result += all_prefixes_and_suffixes(w)
        except TypeError:
            return [W]
    return list(flatten(result))


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def matrix_product(a, axis=0):
    if axis == 1:
        return matrix_product(a.T, axis=0)
    elif axis == 0:
        out = a[0,:].copy()
        for other_row in a[1:,:]:
            out = out.multiply(other_row)
        return out.T
    else:
        raise IndexError("axis out of bounds")


def sparse_divide_nonzero(a, b):
        inv_b = b.copy()
        inv_b.data = 1 / inv_b.data
        return a * inv_b


def sparse_log_nonzero(a):
        a = a.copy()
        a.data = np.log(a.data)
        return a


def substring_feature_coefficient(df, target='form', ignore=None, n_affixes = None, n_feature_sets = 100, min_affix_freq = 100, min_feature_set_freq = 100, level = 'token', substring_extraction=all_prefixes_and_suffixes):

    assert level in ('type', 'token')
    print('Extracting paradigms with:')
    print('\tTarget:', target)
    print('\tIgnoring:', ignore)
    print('\tMax. number of affixes:', n_affixes)
    print('\tMax. number of feature sets:', n_feature_sets)
    print('\tMin. affix frequency:', min_affix_freq)
    print('\tMin. feature set frequency:', min_feature_set_freq)
    print('\tLevel:', level)
    if ignore is not None:
        df = df.drop(ignore, axis=1)
    df = df.drop(df[df['translation'] == ()].index)
    df['parents'] = df['parents'].apply(lambda x: '_'.join(x.split('_')[:-1]))
    def to_string(x):
        if x.name not in (target, 'form'):
            if isinstance(x.iloc[0], str):
                return x.apply(lambda x_i: frozenset({x.name+'='+x_i.replace(':', '_')}))
            else:
                try:
                    return x.apply(lambda x_i: frozenset({x.name+'='+str(x_j).replace(':', '_') for x_j in x_i}))
                except TypeError:
                    return x.apply(lambda x_i: frozenset({x.name+'='+str(x_i).replace(':', '_')}))
        else:
            return x
    df = df.apply(to_string)
    if level == 'type':
        df = df.drop_duplicates()

    affixes = df[target].apply(lambda x: Counter(substring_extraction(x)))
    df['_affixes_'] = affixes
    features = []
    for col_name in df.columns:
        if col_name in (target, 'form', '_count_', '_affixes_'):
            continue
        L = df[col_name].to_list()
        if type(L[0]) in [set, frozenset, list, tuple]:
            L = [Counter({str(y) for y in x}) for x in L]
        else:
            L = [Counter({str(x)}) for x in L]
        features.append(L)
    new_df = []
    for w in zip(*features):
        S = w[0]
        for s in w[1:]:
            S += s
        new_df.append(S)
    df['_features_'] = new_df

    affixes = df['_affixes_']
    features = df['_features_']

    print('Total number of words:', df.shape[0])

    affixes_dv = DictVectorizer(sort=False)
    affixes = affixes_dv.fit_transform(affixes)
    print('Total number of affixes:', affixes.shape[1])
    affixes_to_keep = np.array(affixes.sum(axis=0)>=min_affix_freq)[0]
    affixes = affixes[:, affixes_to_keep]
    affixes_sort_key = np.array(np.argsort(affixes.sum(axis=0)))[0][::-1]
    affixes = affixes[:, affixes_sort_key][:, :n_affixes]
    affixes_columns = np.array(affixes_dv.get_feature_names())
    affixes_columns = affixes_columns[affixes_to_keep]
    affixes_columns = affixes_columns[affixes_sort_key][:n_affixes]
    print('\tNumber of affixes selected:', affixes.shape[1])


    features_dv = DictVectorizer(sort=False)
    features = features_dv.fit_transform(features)
    print('Number of distinct features:', features.shape[1])
    redundant_columns = np.array(features.sum(axis=0) < features.shape[0])[0]
    features = features[:, redundant_columns] # remove columns that are the same for all
    features_columns = np.array(features_dv.get_feature_names())[redundant_columns]
    features_to_keep = np.array(features.sum(axis=0)>=min_feature_set_freq)[0]
    features = features[:, features_to_keep]
    features_columns = features_columns[features_to_keep]
    features_sort_key = np.array(np.argsort(features.sum(axis=0)))[0][::-1]
    features = features[:, features_sort_key][:, :]
    features_columns = features_columns[features_sort_key][:]
    print('\tNumber of features selected:', features.shape[1])

    group_keys = Counter()
    for word in features:
        word = features_columns[(word>0).toarray()[0]]
        ps = powerset(set(word))
        for subset in ps:
            group_keys[tuple(sorted(subset))] += 1
    print('Number of distinct feature sets:', len(group_keys))
    for key, count in dropwhile(lambda key_count: key_count[1] >= min_feature_set_freq, group_keys.most_common()):
        del group_keys[key]
    print('\tNumber of distinct feature sets exceeding minimum frequency:', len(group_keys))

    encountered_common_sets = [tuple()]
    group_key_df = None
    group_key_df_columns = []
    print('Processing feature sets...')
    for i, group_key in enumerate(group_keys.most_common()):
        if len(group_key_df_columns) == n_feature_sets:
            break
        group_key, freq = group_key
        if group_key in encountered_common_sets:
            continue
        pred = matrix_product(features[:, np.in1d(features_columns, group_key)], axis=1)
        if pred.sum() == 1:
            continue
        common_set = matrix_product(features[(pred==1).toarray()[:,0]])
        common_set = features_columns[(common_set>0).toarray()[:,0]]
        common_set = tuple(sorted(common_set))
        if common_set in encountered_common_sets:
            continue
        encountered_common_sets.append(common_set)
        if group_key_df is None:
            group_key_df = pred == 1
        else:
            group_key_df = sparse.hstack([group_key_df, pred==1], dtype=sparse.csr_matrix)
        group_key_df_columns.append(common_set)
    print('Number of feature sets selected:', group_key_df.shape[1])

    features_array = group_key_df #shape = N(words/rows), N(feature bundles)
    affixes_array = affixes #shape = N(words/rows), N(substrings)
    features_array = features_array.astype(int)
    affixes_array = affixes_array.astype(int)

    x = sparse_package.COO.from_scipy_sparse(affixes_array)
    y = sparse_package.COO.from_scipy_sparse(features_array)
    xy = x.T.reshape((x.shape[1], 1, x.shape[0])) * y.T.reshape((1,) + y.shape[::-1])
    p_x = x.sum(axis=0) / x.shape[0]
    p_y = y.sum(axis=0) / y.shape[0]
    p_xy = xy.sum(axis=2) / xy.shape[2]
    cond_p_xy = sparse_divide_nonzero(p_xy, p_y.reshape((1,) + p_y.shape))
    pmi = sparse_log_nonzero(sparse_divide_nonzero(cond_p_xy, p_x.reshape(p_x.shape + (1,))))
    res = cond_p_xy * pmi

    print('Number of non-zero values:', res.nnz)
    sorted_values = res.coords[:,(res.data).argsort()]
    sorted_features = np.array(group_key_df_columns)[sorted_values[1]]
    sorted_affixes = np.array(affixes_columns)[sorted_values[0]]
    sorted_values = np.sort(res.data)
    res = pd.DataFrame({'features': sorted_features, 'affix': sorted_affixes, 'value': sorted_values})
    res = res.dropna()
    res = res.drop(res[res['value'] <= 0].index)
    res = res.tail(1000)
    new_res = pd.DataFrame([res.iloc[-1]])
    print('Taking top 1000 and cleaning...')
    for index, row in res[::-1].iterrows():
        changed = False
        for other_index, other_row in new_res.iterrows():
            contains_affix = row['affix'] == other_row['affix']
            if contains_affix == False:
                if row['affix'][0] == '-':
                    contains_affix = other_row['affix'].endswith(row['affix'][1:])
                elif row['affix'][-1] == '-':
                    contains_affix = other_row['affix'].startswith(row['affix'][:-1])
            contain_set = set(row['features']) <= set(other_row['features'])
            if contain_set and row['value'] < other_row['value'] and contains_affix:
                break
            elif contain_set and row['value'] == other_row['value']:
                inverse_contains_affix = row['affix'] == other_row['affix']
                if inverse_contains_affix == False:
                    if other_row['affix'][0] == '-':
                        inverse_contains_affix = row['affix'].endswith(other_row['affix'][1:])
                    elif other_row['affix'][-1] == '-':
                        inverse_contains_affix = row['affix'].startswith(other_row['affix'][:-1])
                if contains_affix or inverse_contains_affix:
                    longest_affix = max([row, other_row], key = lambda r: len(r['affix'].strip('-')))
                    new_res.loc[other_index] = longest_affix
                    changed = True
        else:
            if not changed:
                new_res = new_res.append(row)
    new_res = new_res.drop_duplicates()
    print('Number of feature set-affix pairs found:', new_res.shape[0])
    print('Features-affixes associations:')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None, 'display.expand_frame_repr', False):
        print(new_res[::-1].to_string(index=False))
    print()




lang_pair = ('en', 'hu')
write = True
data_location = '../Data/'
output_location = '../Output/'


if __name__ =="__main__":
    src, trg = lang_pair
    if write:
        f_name = output_location + "AAA_" + src + '-' + trg + '.txt'
        f = open(f_name, 'w', encoding='utf8')
        sys.stdout = f
    df = read_data(src, trg, path = data_location, maximum=1000, nested_feats=True, include_children=True, include_parents=True)
    # substring_feature_coefficient(df, target='translation', ignore=['parents', 'ancestor_cross', 'descendant_cross', 'cousin_cross'], level='type')
    substring_feature_coefficient(df, target='translation', ignore=['ancestor_cross', 'descendant_cross', 'cousin_cross'], level='type', min_affix_freq = 100, min_feature_set_freq = 100)
    if write:
        f.close()
