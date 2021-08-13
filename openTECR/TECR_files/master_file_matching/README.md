## Filename = Description

# Raw files
-> 2021-08-04_vetted&reorganized_TECR.csv = The raw CSV with like-columns combined and renamed for clarity. \
-> TECRDB_Elad_Noor.csv = The raw CSV of Elad Noor's TECR data that he used in developing the component contribution method of eQuilibrator. 


# Manual curation files
-> 2021-08-12_unmatched_TECR_datums.json = A dictionary of the datums from Elad Noor's scraped TECR data that failed to programmatically match with datums from our TECr data. Each dictionary entry corresponds with an unmatched datum and the values of each entry provide the reasons for why each candidate master_file datum failed to completely match with the datum from Elad's file. \
-> Manual_curation.txt = Each of the failed matches in the aforementioned dictionary were manually curated. The resolution of the failed match is provided, as well as the assigned match to the datum from Elad's file.

# Notebook
-> 2021-08-11_master_file_creation.ipynb = The Notebook and complete set of codes that generated the master TECR file. Intermediate files are exported and imported through the execution of the Notebook to provide modularity through the process.