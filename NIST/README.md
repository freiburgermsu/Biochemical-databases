# NIST Thermodynamics of enzyme-catalyzed reactions
The NIST database was processed through the files and Notebook codes of this folder. The file output CSV and JSON files are provided in the main folder of this repository.

## Scraping
The "2021-02-16_APF_NIST web scraper and documentation_03.ipynb" Notebook scraped the database. The website was scraped in 50 segments, which maintained the accuracy of the scraped data. Inaccuracies were observed to compound proportionally with the size of the scraped segments.

## Processing
The "2021-02-16_APF_NIST web scraper and documentation_03.ipynb" Notebook processed the scraped data. The 50 scraped segments were combined into the "2021-02-15_APF_vetted complete NIST database 1-50.csv" file. The common columns of the combined CSV file were consolidated and the enzyme names were extracted from the static "Enzyme Thermodynamic Database.html" file to generate the final "2021-03-21_vetted + reorganized NIST_1.csv" file of the main page of the repository. The final CSV file was further processed through the "2021-03-01_APF_averaging the data_03.ipynb" Notebook into the "2021-03-21_APF_NIST consolidated_01.json" file that is provided in the main page of the repository.
