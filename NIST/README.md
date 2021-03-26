# NIST Thermodynamics of enzyme-catalyzed reactions
The NIST database is represented through the files and code Notebooks of this folder. The file output CSV and JSON files the NIST database are provided in the main folder of this repository.

## Scraping
The "2021-02-16_APF_NIST web scraper and documentation_03.ipynb" Notebook contains the code for scraping the database website. The website was scraped in 50 sections to maintain accuracy of the scraped data, where the extent of inaccuracies in the scraped data was proportional with the size of the scraped sections. 

## Processing
The "2021-02-16_APF_NIST web scraper and documentation_03.ipynb" Notebook processed thr scraped data. The 50 scraped sections were combined into the "2021-02-15_APF_vetted complete NIST database 1-50.csv" file. The common columns of the CSV file were consolidated and the enzyme names were extracted from the static "Enzyme Thermodynamic Database.html" file into the final "2021-03-21_vetted + reorganized NIST_1.csv" file of the main page of the repository. The CSV file was further processed through the "2021-03-01_APF_averaging the data_03.ipynb" Notebook into the "2021-03-21_APF_NIST consolidated_01.json" file that is provided in the main page of the repository. 
