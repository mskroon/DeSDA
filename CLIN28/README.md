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

Is a modular script for the method that uses Tree Edit Distance (TED) as a measure.

