# OES-Spectra-Analysis

Python scripts with GUI for OES spectra analysis

Input files:
*.csv, *.asc, *.spk, *.Spk (both from SpexHex VisualBasic program)

Output files:
*_raw.csv (Raw data of a spectrum),
*_processed.csv (processed data of a spectrum),
batch-analysis files (default: _batch.ba) including characteristic values of multiple files


## Installation of dependencies
Using the console, navigate to the home directory of the application. Now navigate to /dependencies. You can run the command `python setup.py install` in each subdirectory, so each package, e.g.
1. cd natsort
1. python setup.py install
1. cd ..


## Fitting

Please note, that the filename of a fitting has to end with '_fitting.yml'. This ending can be edited in the config.yml-file.
