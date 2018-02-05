# CLIN28

This folder contains files for research published on CLIN28 on the the development of a syntactic filter that automatically selects parallel sentences that are syntactically comparable.



## main.py

Runs all different methods and draws a graph with a ROC-curve for all methods (also reporting on the AUC score for all methods). It will also return the best threshold, as calculated as the point with the smallest Euclidean distance to the top left corner as well as the point where Youden's J statistic is highest.

All methods take the `en-nl.syn.train` file as input. Some additional models and training-data files are hard-coded. Refer to lines 12 to 16, and change them accordingly.

## levenshtein.py

Is a modular script for the method that uses Levenshtein distance on POS-tags.

An option is to remove stop- and funtion words or not. If `True`, it removes all words that are in the `nltk` stopwords corpus for the language in question -- after which it will calculate the Levenshtein distance on the remaining POS-tags. **For now removing stop- and funtion words is hard-coded to deal with English as source language and Dutch as target language.** If you want to change it to another language (pair), refer to lines 32 and 33, and change accordingly.

## senlen_ratio.py

Is a modular script for the method that uses sentence-length ratio as a measure.

Sentence-length ratio is defined such that it will never be lower than `1`.

An option is to remove stop- and funtion words or not. If `True`, it removes all words that are in the `nltk` stopwords corpus for the language in question -- after which it will calculate the sentence-length ratio based on the remaining words. **For now removing stop- and funtion words is hard-coded to deal with English as source language and Dutch as target language.** If you want to change it to another language (pair), refer to lines 32 and 33, and change accordingly.

## zhang_shasha_UD.py

Is a modular script for the method that uses Tree Edit Distance (TED) as a measure. It applies Zhang and Shasha's (1989) TED algorithm for ordered trees on two Universal Dependencies parses, which are obtained using Straka and Straková's (2017) `udpipe`. **This method therefore requires two UD models to parse the sentences** (available through [`udpipe`'s webpage](http://ufal.mff.cuni.cz/udpipe). 

Tree nodes are represented as a string containing the POS-tag as well as its dependency relation to its head. Dependency relations are split if it contains a `:` (as to generalize over cases such as `nsubj` and `nsubj:pass`), in which case it only takes the part before the `:`. Morphological features are represented as nodes, as well, with names identical to features in CoNLL-U format (e.g. `Case=Acc`). Edges do not have a value, but do have a direction.

The method has two options: to remove stop- and function words and to ignore morphology.

- If removing stop- and function words is set to `True`, it removes all words that are in the `nltk` stopwords corpus for the language in question after `udpipe` has parsed the sentences (unless it is the root of the tree, in which case it is left in place). If a removed word, i.e. node, has any children, its children will instead have an edge to the removed node's head. **For now removing stop- and funtion words is hard-coded to deal with English as source language and Dutch as target language.** If you want to change it to another language (pair), refer to lines 76 and 77, and change accordingly. 

- If ignoring morphology is set to `True`, the algorithm will ignore morphological features, meaning that morphological features will not be represented as nodes in the parsed dependency tree.

## networkx_GED.py

Is as modular script for the method that uses `networkx 2.1`'s Graph Edit Distance (GED) algorithm, which is an implementation of Abu-Aisheh et al.'s (2015) exact GED algorithm. The method takes the GED between two `udpipe` (Straka and Straková, 2017) parses. **This method therefore requires two UD models to parse the sentences** (available through [`udpipe`'s webpage](http://ufal.mff.cuni.cz/udpipe). 

Graph nodes are represented as a Python dictionary, containing POS-tag and morphological features. Edges have the value of the dependency relation between head and child. 

Node substitution cost is defined as the number of items in the node dictionaries that are different (in terms of items added, items removed or items assigned another value). Edge substitution cost is defined as `1` if the edge's label is different. Node and edge instertion and deletion are defined as `1`.

The method has four options: to remove stop- and function words, to ignore morphology, to treat morphology as nodes and to use tf-idf weighting in node instertion, deletion and substitution costs.

- If removing stop- and function words is set to `True`, it removes all words that are in the `nltk` stopwords corpus for the language in question after `udpipe` has parsed the sentences (unless it is the root of the tree, in which case it is left in place). If a removed word, i.e. node, has any children, its children will instead have an edge to the removed node's head. **For now removing stop- and funtion words is hard-coded to deal with English as source language and Dutch as target language.** If you want to change it to another language (pair), refer to line 145, and change accordingly. 

- If ignoring morphology is set to `True`, the algorithm ignores morphological features, meaning that morphological features will not be represented as items in the node dictionaries. This option is incompatible with the option to treat morphology as nodes.

- If treating morphology is set to `True`, the algorithm does not add morphological features to the node dictionaries, but instead adds nodes to the graph with their value (e.g. `Acc`) as POS-tag. The edges leading to them will have the morphological feature (e.g. `Case`, in lower case, so that the algorithm will treat syntactic relation `case` and morphological feature `Case` as the same) as their label. Morphological nodes also receive CoNLL-U format features as items in their dictionary for possible `tf-idf` weight lookup.

- If tf-idf weighting is set to `True`, it calculates `idf` values for all **lemmas** (and morphological features, for when morphology is treated as nodes) for both languages, and redefines node insertion and deletion cost as the lemmas' `tf-idf` weight -- very frequent lemmas are therefore cheaper to insert or delete. Node substitution cost is redefined as the number of items in the node dictionaries that are different (in terms of items added, items removed or items assigned another value) times the average between the lemmas' `tf-idf` weights of the nodes in question. `tf-idf` is defined as (1 + \log(f_{f,d})) * log(\frac{N}{n_t}), using log normalization in the `tf` calculation and normal `idf` -- this way of calculating `tf-idf` has shown to be most effective.
