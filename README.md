# DeSDA

Welcome to the working repository of my PhD research on the automatic detection of syntactic difference (DeSDA). All tools that I developed, as well as datasets that I compiled, for the purposes of my PhD research have been uploaded here, along with relevant output. My dissertation is yet to be published.

This repository consists of three main folders, corresponding to the central chapters of my dissertation.

## Chapter 2 - Filter

The folder Chapter 2 - Filter conatins the tools and data described in Chapter 2 of my dissertation and in [Kroon, Barbiers, Odijk and van der Pas (2019)](https://benjamins.com/catalog/avt.00029.kro).

The folder contains two subfolders:

### Data

The [`Data/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Data) folder contains two types of relevant files types:

- `*.raw` files (e.g. [`de-en.raw`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Data/de-en.raw)) consist of 400 sentence pairs from Koehn's (2005) [Europarl corpus](https://www.statmt.org/europarl/) (of the two languages indicated by the language abbreviations in the file name) separated by a tab. All words have been POS tagged (`word|POS`) with the POS tags having been taken directly from the Europarl corpus metadata. These metadata tags have been translated into [Universal Dependencies](https://universaldependencies.org) (Nivre et al. 2016) using the files in [`Data/tagset_translations/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Data/tagset_translations).
- `*.train` files (e.g. [`de-en.train`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Data/de-en.train)) contain the 400 sentence pairs from the `*.raw` files with a label (`Y|N`) for whether the sentence pair is syntactically comparable or not.

The folder furthmore contains [`UDPipe_models/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Data/UDPipe_models), containing models for [UDPipe](https://github.com/ufal/udpipe) (Straka and Straková 2017), a dependency parser for UD, for convenience.

### Tools

The [`Tools/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Tools) folder contains all the relevant code to run the filters as described in Chapter 2 of my PhD dissertation and in [Kroon, Barbiers, Odijk and van der Pas (2019)](https://benjamins.com/catalog/avt.00029.kro)..

- [`AUC_evaluator.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/AUC_evaluator.py) is used to automatically find the best parameter settings of each individual filter based on the `*.train` files (see above). The variables (which data to use and which UDPipe models to use) are changed within the file. The code reports on the AUC and the best threshold setting based on Youden's J statistic ([Youden 1950](https://acsjournals.onlinelibrary.wiley.com/doi/pdf/10.1002/1097-0142(1950)3%3A1%3C32%3A%3AAID-CNCR2820030106%3E3.0.CO%3B2-3)) and the Euclidean distance for every parameter setup (described in Chapter 2). The script makes use of some multiprocessing, and relies on [`levenshtein.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/levenshtein.py), [`senlen_ratio.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/senlen_ratio.py) and [`networkx_GED`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/networkx_GED.py). Unfortunately, the output is too large to be uploaded.
- [`AUC_evaluator.logreg.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/AUC_evaluator.logreg.py) is used to automatically find the best parameter settings of the logistic regression filter based on the `*.train` files (see above). The variables (which data to use and which UDPipe models to use) are also changed within the file. This script reports on the AUC, but not the best threshold setting (which is always 50%; the AUC is calculated to be able to compare the results). The script also makes use of some multiprocessing, and relies on [`levenshtein.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/levenshtein.py), [`senlen_ratio.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/senlen_ratio.py) and [`networkx_GED.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/networkx_GED.py). Unfortunately, the output is too large to be uploaded.
- as mentioned, [`levenshtein.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/levenshtein.py), [`senlen_ratio.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/senlen_ratio.py) and [`networkx_GED.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/networkx_GED.py) are necessary to automatically find the best parameter setup for the filters using the two scipts described above.
- [`levenshtein_filter.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/levenshtein_filter.py), [`senlen_ratio_filter.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/senlen_ratio_filter.py) and [`networkx_GED_filter.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/networkx_GED_filter.py), on the other hand, take manually set parameters (changed in the file), and take the `*.raw` files (see above) as input, outputting the dataset with syntactically incomparable sentence pairs filtered out.
- [`logreg_filter.py`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Tools/logreg_filter.py) is the logistic regression filter. It allows for the parameters of the filters it uses to be set manually (changed in the file), and uses `*.train` files (see above) to train a classifier, and to filter out syntactically incomparable sentence pairs from it.

## Chapter 3 - MDL

The folder Chapter 3 - MDL contains the tools, data and output of the developed and described tools from Chapter 3 of my PhD dissertation.

## Chapter 4 - Alignment

The folder Chapter 4 - Alignment contains the tools, data and output of the developed and described tools from Chapter 4 of my PhD dissertation.
