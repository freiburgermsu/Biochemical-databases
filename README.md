# Biochemical-databases
Accurate biochemical models require an abundance of biochemical data. We have amassed biochemical data through the Python Notebook codes and files of this repository. The intention of the data is to refine the parameters of kinetic models of bacterial biochemistry.

## NIST
The NIST folder contains the files and codes that processed the NIST Thermodynamics of Enzyme-catalyzed Reactions database. The final data exists in the "2021-03-21_APF_NIST consolidated_01.json" and the "2021-03-21_vetted + reorganized NIST_1.csv" files.

## Karr et al.
The Karr et al. folder contains the files and codes that processed the work of [Karr et al., 2012](https://doi.org/10.1016/j.cell.2012.05.044). The data was primarily acquired by the exporting JSON files from the WholeCellKB.org website, with complementary data from scraping the [WholeCellKB.org website](wholecellkb.org) and with the supplementary excel file from the 2012 publication. The final data exists in the "2021-03-25_APF_WCKB reactions + references.json" file.

# ModelSEED
[ModelSEED](https://modelseed.org/biochem/reactions) is a prominent thermodynamic database. The ModelSEED folder contains the files and codes that combined the thermodynamically described reactions and the corresponding compounds from the NIST and Karr et al. datasets in compliance with the ModelSEED contribution requirements. The compound IDs will be matched with the KEGG database to remove ambiguity of the described reactions and the corresponding compounds. 
