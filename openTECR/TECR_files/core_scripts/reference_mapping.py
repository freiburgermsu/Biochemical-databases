# import modules
from datetime import date
import httpx
import pandas
from io import StringIO
from more_itertools import chunked
from tqdm.notebook import tqdm
import re

CHUNK_SIZE = 100


class reference_mapping():
    def __init__(self):
        pass
        
    def create_mappings(self, mappings_path, export = False):
        from pymed import PubMed
        
        # load the CSV file and 
        req = httpx.request("GET", mappings_path)
        s = StringIO(req.content.decode("UTF-8"))
        tecr_refs = pd.read_csv(s)
        tecr_refs.head()

        # load references from PubMed
        tecr_refs_with_pubmed_id = tecr_refs[~pd.isnull(tecr_refs.pmid)].copy()
        tecr_refs_with_pubmed_id["pmid"] = tecr_refs_with_pubmed_id.pmid.astype(int).astype(str)
        print(f"Collected {tecr_refs_with_pubmed_id.shape[0]} PubMed IDs")

        # parse the references for DOIs
        pubmed = PubMed(tool="MyTool", email="elad.noor@weizmann.ac.il")

        data = []
        with tqdm("downloading metadata from PubMed", total=tecr_refs_with_pubmed_id.shape[0]) as pbar:
            for rows in chunked(tecr_refs_with_pubmed_id.itertuples(), CHUNK_SIZE):
                pubmed_ids = " ".join([str(r.pmid) for r in rows])
                results = pubmed.query(pubmed_ids)
                for paper in results:
                    try:
                        doi = paper.pubmed_doi
                    except AttributeError:
                        doi = None

                    pmid = paper.pubmed_id.split("\n")[0]
                    pbar.set_description_str(f"pubmed ID {pmid}")
                    authors = ", ".join([d["lastname"] + (" " + d["firstname"] if d["firstname"] else "") for d in paper.authors])
                    data.append((str(pmid), doi, paper.publication_date.year, authors, paper.abstract))
                pbar.update(len(rows))

        # export the parsed information into a new CSV
        _df = pd.DataFrame(data=data, columns=["pmid", "doi", "year", "authors", "abstract"])
        self.mappings = _df.join(tecr_refs_with_pubmed_id.set_index("pmid"), on="pmid", lsuffix="_from_pubmed", rsuffix="_from_robert")
        
        if export:
            self.mappings.to_csv("references_with_abstracts.csv")

    @staticmethod
    def apply_mapping(master_file, mappings, reference_ids_column, doi_column, pmid_column, export = False):
    
        # import the master_file and reference_file
        for column in master_file:
            if re.search('Unnamed', column):
                del master_file[column]
            if column =='Reference ID:':
                master_file[column] = [re.sub('(_.+)', '', str(entry)) for entry in master_file[column]]

        # DOI and PMID columns are added to the master_file
        new_column = [' ' for row in range(len(master_file))]
        master_file.insert(6, 'PMID', new_column)
        master_file.insert(7, 'DOI', new_column)

        reference_ids = mappings[reference_ids_column]
        references_added = 0
        for index, reference in reference_ids.iteritems():
            if (mappings.at[index, 'pmid'] or mappings.at[index, doi_column]) not in [' ']:
                reference = re.sub('(_.+)', '', reference)
                matching_master_subset = master_file.loc[master_file['Reference ID:'] == reference]

                for master_index, match in matching_master_subset.iterrows():
                    master_file.at[master_index, 'PMID'] = mappings.at[index, pmid_column]
                    master_file.at[master_index, 'DOI'] = mappings.at[index, doi_column]

                    references_added += 1

        print(f'References added to {references_added} datums')

        # export the indentifier-ingrained CSV
        if export:
            master_file.to_csv(f'{date.today()}_mapped_master.csv')
            
        return master_file