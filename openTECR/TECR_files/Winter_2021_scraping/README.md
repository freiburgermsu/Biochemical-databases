## Filename = description

## Raw data
-> 2021-05-06_concatenated_TECR_01.csv = The raw CSV of scraped TECR enzymes \
-> Enzyme Thermodynamic Database.html = The HTML of TECR that is used in the Notebook codes to parse and scrape the database content.

## Processed data
-> 2021-08-04_TECR_consolidated.json = A JSON of consolidated TECR data \
-> 2021-08-04_TECR_reactions_in_ModelSEED.json = A JSON of all enzymes and their respective sets of reactions. The reactions are partitioned into one of two categories: either 1) all of the reaction compounds are completely described by ModelSEED IDs, which are coupled with TECR IDs according to the list index; or 2) at least one reaction is undescribed by ModelSEED IDs, which prevents the reaction from being conventionally matched in ModelSEED. The reaction strings for category 1) are provided in the ModelSEED convention, while the reaction strings in category 2) are provided in the original TECR format, since the reaction could not be converted into ModelSEED.\
-> 2021-08-10_master_TECR_1.csv = The raw CSV with all content of our scraped TECR data and Elad Noor's scraped TECR data. A "standard_id" column is provided that corresponds to the index of Elad Noor's file. This unambiguously identified TECR datum and provided a means of matching our scraped data with Elad Noor's scraped data. 


## Notebooks
-> 2021-07-05_TECRDB_scraping&ModelSEED_contribution.ipynb = A Notebook that contains the codes for scraping TECR, consolidating the data, combining the data with Elad Noor's data that was used for eQuilibrator, and processing the data into an amenable format for ModelSEED contribution. The above files are generated through the codes of the Notebook. 
