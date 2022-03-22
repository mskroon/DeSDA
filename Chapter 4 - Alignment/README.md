# Chapter 4 - Alignment

This folder contains all the relevant code and data to recreate the experiments from Chapter 4 of my PhD dissertation.

## Tools

```Tools``` contain the DGAE, GTI and AAA, as well as a simple tokenizer on which the three tools depend. Also uploaded is a UDPipe model for convenience ([ParTUT; Sanguinetti and Bosco 2015](https://github.com/UniversalDependencies/UD_English-ParTUT); [Straka and Straková 2017](https://github.com/ufal/udpipe)).

All three tools have a default
```
data_location = '../Data/'
output_location = '../Output/'
```
which works for the architecture for this folder, but the user is free to change it to their likings.

Tools can also be forced not to write the output to a file by setting the ```write``` variable to ```False```.

Apart from that, AAA takes a variable ```lang_pair```, referring to the language abbreviations for the input. Note that these abbreviations must be identical to the abbreviations used in the ```Data``` folder.

The same holds true for DGAE and GTI, but as the first element of the ```setup``` variable. The second element corresponds to the attributes over which the data will be (pre-)grouped, and can be any collection (including the empty set) of attributes in the data, such as ```pos```, ```deprel```, ```translation```, ```feats``` or ```children```.

## Data

The ```Data``` folder contains two subfolders: ```python``` and ```en-hu```.

```python``` contains an English and Hungarian Bible (from [Christodoulopoulos and Steedman 2015](https://github.com/christos-c/bible-corpus)), with one verse ID and verse per line, but only those verses that are present in both versions of the Bible. The script ```xml_aligner.py``` can be used to align the XML Bibles from Christodouloupoulos and Steedman (2015) such that the output contains only the verses present in both translations. The actual XML files have not been uploaded.

```en-hu``` contains the English-Hungarian input (```en-hu.eflomal.txt```) and output (the rest) of [```eflomal```](https://github.com/robertostling/eflomal) (Östling and Tiedemann 2016), which is used in Chapter 4. These word alignments are necessary for all three tools.

## Output

Finally ```Output``` contains the output for AAA and DGAE in three different setups. 

Unfortunately, the GTI output is too large to upload on GitHub. However, those who are intested, please contact me.
