# Filename = description

## Raw data
-> 2021-05-06_concatenated_TECR_01.csv = The raw CSV of scraped TECR enzymes \
-> 2021-08-04_vetted&reorganized_TECR.csv = The raw CSV with like columns combined and renamed for clarity. \

## Processed data
-> 2021-08-04_TECR_consolidated.json = A JSON of consolidated TECR data \
-> 2021-08-04_TECR_reactions_in_ModelSEED.json = A JSON of all enzymes and their respective sets of reactions. The reactions are partitioned into one of two categories: either 1) all of the reaction compounds are completely described by ModelSEED IDs, which are coupled with TECR IDs according to the list index; or 2) at least one reaction is undescribed by ModelSEED IDs, which prevents the reaction from being conventionally matched in ModelSEED. The reaction strings for category 1) are provided in the ModelSEED convention, while the reaction strings in category 2) are provided in the original TECR format, since the reaction could not be converted into ModelSEED.\ 


## Notebooks
-> 2021-07-05_TECR_scraping_ModelSEEDformatting_03.ipynb = A Notebook that contains the codes for scraping TECR and processing the data into an amenable format for ModelSEED contribution. The above files are generated through the codes of the Notebook. \
