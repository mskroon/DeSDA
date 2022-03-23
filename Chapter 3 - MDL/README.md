# Chapter 3 - MDL

In this folder one can find all the relevant files for the research put forth in Chapter 3 of my PhD dissertation.

The research makes use of [UDPipe](https://github.com/ufal/udpipe) (Straka and Straková 2017) and [SQS](http://adrem.uantwerpen.be/sqs) (Tatti and Vreeken 2012).

The research can be recreated as follows:

## 1. Parsing

As said, UDPipe is used, and can be called as follows on the relevant data. Not uploaded in this repository are the models, but these can be found [here](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-2898).

```
udpipe --input=horizontal --output=conllu --tag --parse english-ewt-ud-2.3-181115.udpipe Data/raw/Europarl.10k.en > Data/conllu/conllu.en
udpipe --input=horizontal --output=conllu --tag --parse czech-pdt-ud-2.3-181115.udpipe Data/raw/Europarl.10k.cs > Data/conllu/conllu.cs
udpipe --input=horizontal --output=conllu --tag --parse dutch-alpino-ud-2.3-181115.udpipe Data/raw/Europarl.10k.nl > Data/conllu/conllu.nl
```

## 2. Dutch _te_

We noticed that there was an (easily solvable) inconsistency in tagging between English and Dutch. While English verbal particle _to_ was consistently tagged as a particle (PART), its Dutch counterpart _te_ was consistently tagged as a preposition (ADP). This was remedied by manually changing all occurrences of _te_ to a PART when it was directly followed by a verb or auxiliary, because such an inconsistency results in syntactic differences found that are actually spurious. Similar preprocessing was also done for Czech. In other positions the ADP tag was kept, because _te_ can also function as a preposition ('in') or even as a degree morpheme ('too').

In `Tools/` a simple script can be found to do this, and can be called as follows:

```
python te_adp_part.py
```

## 3. Preparing input for SQS

SQS takes specific input. In order to shape the CoNLL-U formatted output of UDPipe into understandable input for SQS, one can call

```
python sqs_input_file_maker_conllu.py ../Data/conllu/conllu.en ../Data/sqs/
python sqs_input_file_maker_conllu.py ../Data/conllu/conllu.cs ../Data/sqs/
python sqs_input_file_maker_conllu.py ../Data/conllu/conllu.te.nl ../Data/sqs/
```

This script prepares the `*.dat` and `*.lab` files found in `Data/sqs/`.

## 4. Running SQS

SQS can be called as follows for each language (change the language abbreviations accordingly):

```
sqs -i Data/sqs/conllu.en.dat -o Data/pattern_files/res.en -m search
sqs -i Data/sqs/conllu.en.dat -o Data/pattern_files/ord.en -m order -p Data/pattern_files/res.en
```

SQS's output can be found in `Data/pattern_files/`.

## 5. Interpreting SQS's output

SQS's output is as specific as its input, and must be translated back in POS tags in order to detect syntactic differences.
This is done with:

```
python sqs_output_interpreter.py ../Data/pattern_files/ord.en ../Data/sqs/conllu.en.lab
```

This creates the `*.trans` files in the `Data/pattern_files/` folder.

## 6. Filtering (optional)

We also investigated the influence of the filter of Chapter 2 on the process of automatically detecting syntactic differences.
Particularly, the GED algorithm was deployed with threshold 4 and was set to ignore all functional material.
The GED filter can be called with:

```
python GED_syn_comp_filter.py
```

This creates the subfolders and the according files in `Data/conllu/`. Variables of the filter are set within the script file.

## 7. Detecting syntactic differences automatically using the Minimum Description Length principle

Finally, differences can be found with:

```
python MDL_difference_detector.py
```

Variables are set within the Python file. Revelant are:
- `setup`, which sets how the script should be run: with or without filtered data (the first character), with or without superpattern subtraction (the second character).	`setup` must be `(NN|NY|YN|YY)`.
- `lang_a` and `lang_b`, which correspond to the language abbreviations used in the `Data/` folder.

The output of `MDL_difference_detector.py` can be found in `Output/`.

## Reference

More information on the automatic detection of syntactic differences using the Minimum Description Length principle can be found in [Kroon, Barbiers, Odijk and van der Pas (2020)](https://www.clinjournal.org/clinj/article/view/109). More details on the GED-based filter can be found in [Kroon, Barbiers, Odijk and van der Pas (2019)](https://benjamins.com/catalog/avt.00029.kro).

When using anything from this repository for your research, please cite:
```
@article{kroon2020detecting,
    title={Detecting syntactic differences automatically using the Minimum Description Length principle},
    author={Kroon, Martin and Barbiers, Sjef and Odijk, Jan and van der Pas, St{\'e}phanie},
    journal={Computational Linguistics in the Netherlands Journal},
    volume={10},
    pages={109--127},
    year={2020}
}
```

When using the GED-based filter, please also cite:
```
@article{kroon2019filter,
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
