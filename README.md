# DeSDA

Welcome to the working repository of my PhD research on the automatic detection of syntactic difference (DeSDA). All tools that I developed, as well as datasets that I compiled, for the purposes of my PhD research have been uploaded here, along with relevant output. My dissertation is yet to be published.

This repository consists of three main folders, corresponding to the central chapters of my dissertation.

## Chapter 2 - Filter

The folder Chapter 2 - Filter conatins the tools and data described in Chapter 2 of my dissertation and in [Kroon, Barbiers, Odijk and van der Pas (2019)](https://benjamins.com/catalog/avt.00029.kro).

The folder contains two subfolders:

### Data

The [`Data/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Data) folder contains two types of relevant files types:

- `*.raw` files (e.g. [`de-en.raw`](https://github.com/mskroon/DeSDA/blob/master/Chapter%202%20-%20Filter/Data/de-en.raw)) consist of 400 sentence pairs from Koehn's (2005) [Europarl corpus](https://www.statmt.org/europarl/) (of the two languages indicated by the language abbreviations in the file name) separated by a tab. All words have been POS tagged (`word|POS`) with the POS tags having been taken directly from the Europarl corpus metadata. These metadata tags have been translated into [Universal Dependencies](https://universaldependencies.org) (Nivre et al. 2016) using the files in [`/Data/tagset_translations/`](https://github.com/mskroon/DeSDA/tree/master/Chapter%202%20-%20Filter/Data/tagset_translations).
- `*.train` files contain the 400 sentence pairs from the `*.raw` files with a label (`Y|N`) for whether the sentence pair is syntactically comparable or not.

The folder furthmore contains `UDPipe_models/`, containing models for [UDPipe](https://github.com/ufal/udpipe) (Straka and Straková 2017), a dependency parser for UD.

## Chapter 3 - MDL

The folder Chapter 3 - MDL contains the tools, data and output of the developed and described tools from Chapter 3 of my PhD dissertation.

## Chapter 4 - Alignment

The folder Chapter 4 - Alignment contains the tools, data and output of the developed and described tools from Chapter 4 of my PhD dissertation.
