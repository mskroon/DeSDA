# Chapter 2 - Filters

In this repository one can find all relevant files for the second chapter of my PhD dissertation, a version of which was already published as

```
@article{Kroon2019,
    title = {A filter for syntactically incomparable parallel sentences},
    author={Kroon, Martin and Barbiers, Sjef and Odijk, Jan and van der Pas, St{\'e}phanie},
    year = 2019,
    journal={Linguistics in the Netherlands},
    volume={36},
    pages={147--161},
    editor = {Janine Berns and Elena Tribushinina},
    doi = {https://doi.org/10.1075/avt.00029.kro},
    publisher={John Benjamins}
}
```

This repository contains two folders:

## Data

The `Data/` folder contains two types of relevant files types:

- `*.raw` files consist of 400 sentence pairs from Koehn's (2005) Europarl corpus (of the two languages indicated by the language abbreviations in the file name) separated by a tab. All words have been POS tagged (`word|POS`) with the POS tags having been taken directly from the Europarl corpus metadata. These metadata tags have been translated into Universal Dependencies (Nivre et al. 2016) using the files in `/Data/tagset_translations/`.
- `*.train` files contain the 400 sentence pairs from the `*.raw` files with a label (`Y|N`) for whether the sentence pair is syntactically comparable or not.

The folder furthmore contains `UDPipe_models/`, containing models for [UDPipe](https://github.com/ufal/udpipe) (Straka and Straková 2017), a dependency parser for UD.

## Tools

The `Tools/` folder contains all the relevant code to run the filters as described in Chapter 2 of my PhD dissertation.

- `AUC_evaluator.py` is used to automatically find the best parameter settings of each individual filter based on the `*.train` files. The variables (which data to use and which UDPipe models to use) are changed within the file. The code reports on the AUC and the best threshold setting based on Youden's J statistic and the Euclidean distance for every parameter setup (described in Chapter 2). The script makes use of some multiprocessing, and relies on `levenshtein.py`, `senlen_ratio.py` and `networkx_GED`. Unfortunately, the output is too large to be uploaded.
- `AUC_evaluator.logreg.py` is used to automatically find the best parameter settings of the logistic regression filter based on the `*.train` files. The variables (which data to use and which UDPipe models to use) are also changed within the file. This script reports on the AUC, but not the best threshold setting (which is always 50%; the AUC is calculated to be able to compare the results). The script also makes use of some multiprocessing, and relies on `levenshtein.py`, `senlen_ratio.py` and `networkx_GED`. Unfortunately, the output is too large to be uploaded.
- as mentioned, `levenshtein.py`, `senlen_ratio.py` and `networkx_GED` are necessary to automatically find the best parameter setup for the filters using the two scipts described above.
- `levenshtein_filter.py`, `senlen_ratio_filter.py` and `networkx_GED_filter`, on the other hand, take manually set parameters (changed in the file), and take the `*.raw` files as input, outputting the dataset with syntactically incomparable sentence pairs filtered out.
- `logreg_filter.py` is the logistic regression filter. It allows for the parameters of the filters it uses to be set manually (changed in the file), and uses `*.train` to train a classifier, and to filter out syntactically incomparable sentence pairs from it.