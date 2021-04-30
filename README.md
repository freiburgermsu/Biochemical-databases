# Biochemical-databases
Accurate biochemical models require an abundance of biochemical data. We have amassed biochemical data from various databases with the intention of applying the data in flux balance analysis (FBA) model parameters. The Python Notebook codes and intermediary and output files are organized into respective folders for each amalgamated database.

## NIST
The NIST folder contains the files for acquiring and processing biochemical data from the NIST Thermodynamics of Enzyme-catalyzed Reactions database. The final data is provided in the "2021-03-21_APF_NIST consolidated_01.json" and the "2021-03-21_vetted + reorganized NIST_1.csv" files.

## Karr et al.
The Karr et al. folder contains the files for acquiring and processing biochemical data from the work of Karr et al.. The body of work is primarily represented by the exported JSON files for the WholeCellKB.org website, which was complemented by webscraping the WholeCellKB.org website and with the supplementary excel file from the [2012 publication from Karr et al.](https://doi.org/10.1016/j.cell.2012.05.044). The final data is provided in the "2021-03-25_APF_WCKB reactions + references.json" file.

## Combined databases
The thermodynamically described reactions and the corresponding compounds from the NIST and Karr et al. datasets were combined. The reaction expressions were first standardized to conform with the contribution criteria of the ModelSEED database. The compound IDs were then matched with the KEGG database to remove ambiguity of the described reactions and the corresponding compounds. The codes and final files from the combined database of thermodynamic information is organized in the ModelSEED folder. 
