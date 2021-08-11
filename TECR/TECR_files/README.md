# Filename = description

## Raw data
-> 2021-05-06_concatenated_TECR_01.csv = The raw CSV of scraped TECR enzymes \
-> 2021-08-04_vetted&reorganized_TECR.csv = The raw CSV with like-columns combined and renamed for clarity. \
-> TECRDB_Elad_Noor.csv = The raw CSV of Elad Noor's TECR data that he used in developing the component contribution method of eQuilibrator. 

## Processed data
-> 2021-08-04_TECR_consolidated.json = A JSON of consolidated TECR data \
-> 2021-08-04_TECR_reactions_in_ModelSEED.json = A JSON of all enzymes and their respective sets of reactions. The reactions are partitioned into one of two categories: either 1) all of the reaction compounds are completely described by ModelSEED IDs, which are coupled with TECR IDs according to the list index; or 2) \ at least one reaction is undescribed by ModelSEED IDs, which prevents the reaction from being conventionally matched in ModelSEED. The reaction strings for category 1) are provided in the ModelSEED convention, while the reaction strings in category 2) are provided in the original TECR format, since the reaction could not be converted into ModelSEED.\
-> 2021-08-10_master_TECR_1.csv = The raw CSV with all content of our scraped TECR data and Elad Noor's scraped TECR data. A "standard_id" column is provided that corresponds to the index of Elad Noor's file. This unambiguously identified TECR datum and provided a means of matching our scraped data with Elad Noor's scraped data. 

## Verification files
-> 2021-08-10_unmatched_TECR_datums.json = A dictionary of the unmatched datums from Elad Noor's scraped TECR data. Each entry corresponds with an unmatched datum and the values of each entry provide the reasons for why each candidate master_file match failed completely match. These files will be rectified manually to establish an encompassing master TECR file. 


## Notebooks
-> 2021-07-05_TECRDB_scraping&ModelSEED_contribution.ipynb = A Notebook that contains the codes for scraping TECR, consolidating the data, combining the data with Elad Noor's data that was used for eQuilibrator, and processing the data into an amenable format for ModelSEED contribution. The above files are generated through the codes of the Notebook. 
