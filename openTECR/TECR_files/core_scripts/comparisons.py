import re



class comparison():
    def __init__(self, scraping_1, scraping_2, scraping_3):
        self.scraping_1 = scraping_1
        self.scraping_2 = scraping_2
        self.scraping_3 = scraping_3
        
        for scraping in [scraping_1, scraping_2, scraping_3]:
            if 'noor' in scraping:
                self.noor_enzymes = set(list(scraping['noor']['enzyme_name']))
                self.noor_references = set(list(scraping['noor']['reference']))
            elif 'du' in scraping:
                self.du_enzymes = set(list(scraping['du']['Reaction']))
                self.du_references = set(list(scraping['du']['Reference_id']))
            elif 'freiburger' in scraping:
                self.freiburger_enzymes = set()
                for enzymes in [df['Enzyme:'] for df in list(scraping.values())]:
                    for enzyme in enzymes:
                        enzyme = str(enzyme).strip()
                        self.freiburger_enzymes.add(enzyme)
                    
                self.freiburger_references = set()
                for references in [df['Reference ID:'] for df in list(scraping.values())]:
                    for reference in references: 
                        if reference not in [' ']:
                            substituted_reference = re.sub('_.+', '', str(reference))
                            self.freiburger_references.add(substituted_reference)
                
    def three_way_comparison(self, analysis):
        comparisons = {}
        
        if analysis == 'enzymes':
            set_1 = self.noor_enzymes
            set_2 = self.du_enzymes
            set_3 = self.freiburger_enzymes
        elif analysis == 'references':
            set_1 = self.noor_references
            set_2 = self.du_references
            set_3 = self.freiburger_references

        comparisons['noor, not in du'] = set_1 - set_2
        comparisons['noor, not in freiburger'] = set_1 - set_3
        comparisons['du, not in noor'] = set_2 - set_1
        comparisons['du, not in freiburger'] = set_2 - set_3
        comparisons['freiburger, not in noor'] = set_3 - set_1
        comparisons['freiburger, not in du'] = set_3 - set_2  

        return comparisons
    
    def bigg_comparison(self, bigg_model_json, master_file):
        # parse the JSON file for reaction EC values
        undescribed_enzymes = {}
        master_enzymes = list(master_file['Enzyme:'])
        total_data_points = []
        for key, value in bigg_model_json.items():
            if key == 'reactions':
                for enzyme in value:
                    for key2, value2 in enzyme.items():
                        if key2 == 'name':
                            enzyme_name = value2
                        if key2 == 'annotation':
                            for source, content in value2.items(): 
                                if source == 'ec-code':
                                    ecs = content
                                    print(enzyme_name, '\t', ecs)
                                    # investigate the master_file for the EC values
                                    enzyme_data_count = 0
                                    for ec in ecs:
                                        mask = master_file['EC Value:'].str.contains(ec)
                                        try:
                                            enzyme_data_count += mask.value_counts()[True]
                                        except:
                                            pass
                                    print(enzyme_data_count)
                                    if enzyme_data_count == 0:
                                        for enz in master_enzymes:
                                            if re.search(enzyme_name.strip(), str(enz).strip(), re.IGNORECASE):
                                                enzyme_data_count += 1
                                        if enzyme_data_count == 0:
                                            undescribed_enzymes[enzyme_name] = ecs
                                        print(enzyme_data_count)
                                    total_data_points.append(enzyme_data_count)
                                    
        print('\n\nundescribed_enzymes', undescribed_enzymes)
        print('\ntotal_enzymes:', len(bigg_model_json['reactions']))
        print('described_enzymes:', len(bigg_model_json['reactions']) - len(undescribed_enzymes))
        print('total data points:', sum(total_data_points))
        print('average datums per enzyme:', sum(total_data_points) / len(total_data_points))
