from to_precision import sci_notation
from datetime import date
from numpy import nan, unique
import pandas
import json
import re

empty = [nan, 'nan', None, ' ', '', 'NaN']
freiburger_index = None

# homogenize the charge format    
def charge_format(master_reaction):                                
    remove_string = re.search('\w(\d\-)', master_reaction).group(1)
    master_reaction = re.sub(remove_string, '-{}'.format(remove_string), master_reaction)
    return master_reaction, remove_string

# add the units of logarithm to the Magnesium concentration
def isnumber(string):
    if string not in ['', ' ', nan]:
        try:
            float(string)
            return True
        except:
            try:
                string.isnumeric()
                return True
            except:
                return False 

class merge_package():
    def __init__(self, master_dataframe, new_dataframe, scraping):
        self.scraping = scraping
        self.master_file = master_dataframe        
        self.new_file = new_dataframe
        self.original_master_file_length = len(self.master_file)
        
    def merge(self, new_enzyme_column_name, new_reference_column_name, manual_curation_csv_path, export = False):
        self.add_new(new_enzyme_column_name, new_reference_column_name)
        self.merge_existing()
        self.incorporate_manual_curation(manual_curation_csv_path, export)
        self.confirm_merging()
        
        return self.master_file
        
    # =================================================================
        
    def add_new(self, new_enzyme_column_name, new_reference_column_name, master_enzyme_column_name = 'Enzyme:', master_reference_column_name = 'Reference ID:', export = False):
        # compare the enzymes
        new_enzymes = set(self.new_file[new_enzyme_column_name])  
        master_enzymes = set()
        for enzyme in self.master_file[master_enzyme_column_name]:
            if enzyme not in empty:
                enzyme = enzyme.strip()
                master_enzymes.add(enzyme)
        
        missing_master_enzymes = self.set_contrast('enzymes', master_enzymes, new_enzymes, 'new file')
        
        # compare the references
        new_references = set(self.new_file[new_reference_column_name])
        master_references = set()
        for reference in self.master_file[master_reference_column_name]:
            if reference not in empty:
                substituted_reference = re.sub('_.+', '', reference)
                master_references.add(substituted_reference)
        
        missing_master_references = self.set_contrast('references', master_references, new_references, 'new file')
        
        print('before', len(self.master_file))
        
        # add new data rows
        self.new_additions = set()
        for new_index, new_row in self.new_file.iterrows():
            new_enzyme = new_row[new_enzyme_column_name]
            new_reference = new_row[new_reference_column_name]
            # add undescribed enzymes and citations
            if new_reference in missing_master_references:
                #print(new_reference)
                # add a new row at the end of master dataframe, according to master column organization
                self.master_file.loc[len(self.master_file.index)] = self.define_row(new_index, new_row, self.scraping)
                self.new_additions.add(new_index)
            elif new_enzyme in missing_master_enzymes:
                #print(new_enzyme)
                # add a new row at the end of master dataframe, according to master column organization
                self.master_file.loc[len(self.master_file.index)] = self.define_row(new_index, new_row, self.scraping)
                self.new_additions.add(new_index)
       
        # format the magnesium potential
        undescribed = list(self.master_file['Experimental conditions'])[self.original_master_file_length + 1 :]
        for row in undescribed:
            if isnumber(row):
                index = list(self.master_file['Experimental conditions']).index(row)
                self.master_file.at[index, 'Experimental conditions'] = '{} = -log[Mg+2]'.format(str(row))

        if export:
            self.master_file.to_csv(f'{date.today()}_master_TECR_1.csv')
            
        print('after', len(self.master_file))
        print('total additions', len(list(self.new_additions)))
        
            
    def merge_existing(self, export = False):
        matched_master_indices = {}
        display_count = 0
        unmatched_entries = 0
        errors_dictionary = {}
        for new_index, new_row in self.new_file.iterrows():
            if new_index not in self.new_additions:
                matched_datum = False

                # define the new values for this datum 
                row = self.define_row(new_index, new_row, self.scraping) # [freiburger_index, du_index, noor_index, add_enzyme, add_kegg_reaction, add_cid_reaction, add_reaction, reference_string, add_reference, add_temperature, add_ph, add_k, km, add_method, buffer, add_pmg, add_ec, solutes_1, solutes_2, ionic_strength_1, add_ionic_strength, enthalpy]
                new_enzyme = row[3]
                new_reaction = row[6]
                new_reference = row[8]
                new_temperature = row[9]
                new_ph = row[10]
                new_k = row[11]

                # determine the set of possible matches
                errors = []
                matching_master_subset = self.master_file.loc[(self.master_file['Enzyme:'] == new_enzyme)]    #  & (master_file['Keq'] == new_k) & (master_file['T [K]'] == new_temperature) & (master_file['pH '] == new_ph)
                for master_index, master_row in matching_master_subset.iterrows():  
                    # remove previously matched rows
                    if master_index in matched_master_indices:
                        error = ''.join([str(x) for x in [master_index, '___','previously matched master_index to the new_index:', '___', matched_master_indices[master_index]]])
                        errors.append(error)
                        continue

                    # define the master values for this datum 
                    master_reference_id, master_reaction, master_temperature, master_ph, master_k = self.define_row(master_index, master_row, scraping_name = 'master')

                    # match the reference
                    if new_reference != master_reference_id:
                        error = ''.join([str(x) for x in [master_index, '___', 'reference', '___', new_reference, '___', master_reference_id]])
    #                     print(error)
                        errors.append(error)
                        continue

                    # match the temperature
                    if (new_temperature and master_temperature) not in empty:
                        new_temperature = re.sub('l', '1', str(new_temperature))
                        master_temperature = re.sub('l', '1', str(master_temperature))
                        if self.rounding(new_temperature) != self.rounding(master_temperature):
                            error = r''.join([str(x) for x in [master_index, '___','temperature', '___', new_temperature, '___', master_temperature]])
    #                         print(error)
                            errors.append(error)
                            continue

                    # match the pH
                    if (new_ph and master_ph) not in empty:
                        new_ph = str(new_ph).strip('?~')
                        master_ph = str(master_ph).strip('?~')
                        if isnumber(new_ph) and isnumber(master_ph):
                            if self.rounding(new_ph) != self.rounding(master_ph):
                                error = r''.join([str(x) for x in [master_index, '___','ph', '___', new_ph, '___', master_ph]])
    #                             print(error)
                                errors.append(error)
                                continue

                    # match the Keq
                    if re.search('\w(\?\w+)', str(master_k)):
                        master_k = re.sub('(\?\w+)', '', str(master_k))

                    if (new_k and master_k) not in empty:
                        new_k = str(new_k).strip('~?')
                        master_k = str(master_k).strip('~?')
                        if isnumber(new_k) and isnumber(master_k):
                            if self.rounding(new_k) != self.rounding(master_k):
                                error = r''.join([str(x) for x in [master_index, '___', 'Keq', '___', new_k, '___', master_k]])
    #                             print(error)
                                errors.append(error)
                                continue

                    # match the reactions 
                    if new_reaction != master_reaction:
                        if re.search('= -\w', master_reaction):
                            remove_string = re.search('=(\s-)\w', master_reaction).group(1)
                            master_reaction = re.sub(remove_string, '-', master_reaction)

                        if new_reaction != master_reaction:
                            if re.search(' -D-', master_reaction):
                                remove_string = re.search('\s(-D-)', master_reaction).group(1)
                                master_reaction = re.sub(remove_string, 'D-', master_reaction, 1)

                            if new_reaction != master_reaction:
                                if re.search('\w\d\-', master_reaction):
                                    loop = True
                                    try:
                                        while loop :
                                            master_reaction, remove_string = charge_format(master_reaction)
                                            if remove_string is None:
                                                loop = False
                                    except:
                                        pass

                                if new_reaction != master_reaction:
                                    if re.search('\(\w\)\-', master_reaction):
                                        master_reaction = re.sub('\(\w\)\-', '', master_reaction)

                                    if new_reaction != master_reaction:
                                        if re.search('-lipoate', master_reaction):
                                            master_reaction = re.sub('(-lipoate)', 'lipoate', master_reaction, 1)

                                        if new_reaction != master_reaction:
                                            error = ''.join([str(x) for x in [master_index, '___', 'reaction', '___', new_reaction, '___', master_reaction]])
    #                                         print(error)
                                            errors.append(error)
                                            continue


                    # define the new data of the master file

                    matched_datum = True
                    matched_master_indices[master_index] = new_index
                    self.redefine_master(master_row, new_row, master_index, new_index)
                    break

                if not matched_datum:
                    print('--> Failed index to match: ', new_index, '___', new_enzyme)
                    unmatched_entries += 1
                    errors_dictionary[new_index] = errors

        # test for standard_id uniqueness and unmatched values
        unique_matched_indices = set()
        for master_index in matched_master_indices:
            if master_index in unique_matched_indices:
                print('repeated entry: ', master_index)
            else:
                unique_matched_indices.add(master_index)
        print('Unmatched indices: ', unmatched_entries)

        # export the unmatched datums
        with open(f'{date.today()}_unmatched_TECR_datums.json', 'w') as output:
            json.dump(errors_dictionary, output, indent = 3)

        # export the combined master file
        if export:
            self.master_file.to_csv(f'{date.today()}_master_TECR_2.csv')
        
       
    def incorporate_manual_curation(self, manual_curation_csv, export = False):
        # import the manual curation file
        headings = []
        for column in manual_curation_csv:
            headings.append(column.strip('\t'))
            for index, row in manual_curation_csv[column].iteritems():
                manual_curation_csv[column].iloc[index] = str(row).strip('\t')
        manual_curation_csv.columns = headings

        # parse the manually curated content
        parsing_errors = []
        self.duplicates = set()
        for index, row in manual_curation_csv.iterrows():
            # characterize the curated datums            
            master_file_ids = [row['Master file index']]
            master_file_ids[0] = master_file_ids[0].strip()
            error = row['Error resolution']
            add = False
            merge = False
            if master_file_ids[0] == 'New' or re.search('sigfig', error):
                add = True

            elif not re.search('--', master_file_ids[0]):            
                merge = True
                # parse the corresponding master_file indices
                if re.search('-', master_file_ids[0]):
                    master_file_ids = master_file_ids[0].split('-')
                    lower = int(master_file_ids[0])
                    upper = int(master_file_ids[1])

                    if lower < upper:
                        id_range = upper - lower
                        master_file_ids = [id + lower for id in range(id_range + 1)]                

                elif re.search(r'\\', master_file_ids[0]):
                    master_file_ids = master_file_ids[0].split('\\')   
                else:
                    master_file_ids = [int(master_file_ids[0])]

            # parse the previously unmatched standard IDs
            new_ids = [row['New index']]
            if re.search('-', new_ids[0]):
                new_ids = new_ids[0].split('-')
                lower = int(new_ids[0])
                upper = int(new_ids[1])
                if lower < upper:
                    id_range = upper - lower
                    new_ids = [id + lower for id in range(id_range + 1)]
            else:
                new_ids = [int(new_ids[0])]

            # add new datums to the master file
            if add or merge:
                for new_id_index in range(len(new_ids)):
                    new_id = new_ids[new_id_index]
                    new_row = self.new_file.iloc[int(new_id)]
                    
                    if new_id not in list(self.master_file[f'{self.scraping}_index']):
                        if add:
                            self.master_file.loc[len(self.master_file.index)] = self.define_row(new_id, new_row, self.scraping)  
                        elif merge:
                            # match the standard id with the master_index
                            match_index = new_ids.index(new_id)
                            print(new_id)
                            print(new_ids)
                            print(match_index)
                            print(master_file_ids)
                            master_index = master_file_ids[match_index]
                            master_row = self.master_file.iloc[int(master_index)]

                            # merge the content of the equilibrator_2008 and master_file for the corresponding standard id
                            self.redefine_master(master_row, new_row, master_index, new_id)
                    else:
                        print(f'--> ERROR: Repeated {self.scraping} index < {new_id} >')

            else:
                # characterize the curated datums            
                error = row['Error resolution']
                if re.search('Duplicate', error):
                    for new_id in new_ids:
                        self.duplicates.add(new_id)
                    print('The {} new_id is a duplicate.'.format(new_ids))
                elif re.search('already', error):
                    print('The {} new_id is already matched.'.format(new_ids))
                else:
                    parsing_errors.append(master_file_ids)
                    print('ERROR: The {} new_id was not captured by the parsing.'.format(new_ids))

        if parsing_errors == []:
            parsing_errors = None
        print('Parsing errors: ', parsing_errors)

        # export the expanded master_file
        if export:
            self.master_file.to_csv(f'{date.today()}_master_TECR_3.csv')
            
    def confirm_merging(self):
        new_indices = set(self.new_file.index)
        merged_indices = set(list(self.master_file[f'{self.scraping}_index']))
        missing_indices = new_indices - merged_indices
        missing_unique_indices = missing_indices - self.duplicates
        if missing_unique_indices == set():
            missing_unique_indices = None
        else:
            missing_unique_indices = sorted(missing_unique_indices)
        
        print('missing unique indices', missing_unique_indices)
        return missing_unique_indices
    
    # ===================================================================================================
        
    def define_row(self, new_index, new_row, scraping_name):
        # define the Noor scraping
        if scraping_name == 'noor':
            du_index = None
            add_id = f'https://w3id.org/related-to/doi.org/10.5281/zenodo.3978439/files/TECRDB.csv#entry{new_index}'
            add_enzyme = new_row['enzyme_name']
            add_kegg_reaction = new_row['reaction']
            add_cid_reaction = None
            add_reaction = new_row['description']
            reference_string = None
            add_reference = new_row['reference']
            add_temperature = new_row['temperature']
            add_ph = new_row['p_h']
            add_k = new_row['K_prime']
            if add_k is nan:
                add_k = new_row['K']
            km = None
            add_method = new_row['method']
            buffer = None
            add_pmg = new_row['p_mg']
            add_ec = new_row['EC']
            solutes_1 = solutes_2 = ionic_strength_1 = None
            add_ionic_strength = new_row['ionic_strength']
            enthalpy = None
            
            return [freiburger_index, du_index, add_id, add_enzyme, add_kegg_reaction, add_cid_reaction, add_reaction, reference_string, add_reference, add_temperature, add_ph, add_k, km, add_method, buffer, add_pmg, add_ec, solutes_1, solutes_2, ionic_strength_1, add_ionic_strength, enthalpy]
        
        elif scraping_name == 'du':
            add_id = f'https://w3id.org/related-to/doi.org/10.5281/zenodo.5494490/files/TableS1_Keq.csv#Keq_{new_index}'
            noor_index = None
            add_enzyme = new_row['Reaction']
            add_kegg_reaction = None
            add_cid_reaction = new_row['Reaction formula in CID format']
            add_reaction = new_row['reaction_string']
            reference_string = None
            add_reference = new_row['Reference_id']
            add_temperature = new_row['T(K)']            
            add_ph = new_row['pH']
            add_k = new_row['K\'']
            km = None
            add_method = new_row['Method']            
            add_buffer = new_row['Buffer/reagents/solute added']
            add_conditions = ' _ '.join([str(new_row['media conditions']), str(new_row['electrolytes']), str(new_row['pMg'])])
            add_conditions = re.sub('_\s+_', '', add_conditions)
            add_ec = new_row['EC value']
            solutes_1 = solutes_2 = ionic_strength_1 = None
            add_ionic_strength = new_row['Ionic strength']
            enthalpy = None
            
            return [freiburger_index, add_id, noor_index, add_enzyme, add_kegg_reaction, add_cid_reaction, add_reaction, reference_string, add_reference, add_temperature, add_ph, add_k, km, add_method, add_buffer, add_conditions, add_ec, solutes_1, solutes_2, ionic_strength_1, add_ionic_strength, enthalpy]
            
        elif scraping_name == 'master':
            master_reference = new_row['Reference:']
            master_method = new_row['Method:']
            master_ec = new_row['EC Value:']
            master_pmg = new_row['Experimental conditions']
            master_ionic_strength = new_row['Ionic strength [mol / dm^3]']
            master_temperature = new_row['T [K]']
            master_ph = new_row['pH ']
            master_k = new_row['Keq']
            master_km = new_row['Km']
            master_reaction = new_row['Reaction:']
            master_reference_id = re.sub('_.+', '', new_row['Reference ID:'])

            if self.scraping == 'noor':    
                master_reaction = re.sub('\u00ce\u00b1|\u00ce\u00b2', '', master_reaction)
                master_reaction = re.sub('\u00cf\u2030', '-w', master_reaction)
            
            return master_reference_id, master_reaction, master_temperature, master_ph, master_k
        
        
            
    # merging values between matched datum
    def redefine_master(self, master_row, new_row, master_index, new_index, verbose = False):

        # print the datum pair for manual inspection
        if verbose:
            announcement = '\nmatched pair:'
            print(announcement, '\n', '='*len(announcement))
            print('new_index', new_index)
            print('master_index', master_index, '\n')

        # match KEGG reactions
        master_kegg = master_row['KEGG Reaction:']
        if master_kegg in empty and self.scraping == 'noor':
            new_kegg = new_row['reaction']
            self.master_file.at[master_index, 'KEGG Reaction:'] = new_kegg

        # match magnesium concentrations
        if self.scraping == 'noor':
            new_pmg = new_row['p_mg']
        elif self.scraping == 'du':
            new_pmg = new_row['pMg']
        master_pmg = master_row['Experimental conditions']
        if str(master_pmg) == '{} = -log[Mg+2]'.format(str(new_pmg)):
            pass            
        elif new_pmg not in empty:
            if master_pmg is nan or master_pmg in empty:
                self.master_file.at[master_index, 'Experimental conditions'] = '{} = -log[Mg+2]'.format(str(new_pmg))
                if verbose:
                    print(master_index, '\t', 'new pmg', '\t', self.master_file.at[master_index, 'Experimental conditions'])
            else:
                self.master_file.at[master_index, 'Experimental conditions'] = " or ".join([str(master_pmg), '{} (-log[Mg+2])'.format(str(new_pmg))]) 
                if verbose:
                    print(master_index, '\t', 'new pmg', '\t', self.master_file.at[master_index, 'Experimental conditions'])            
                
                
#         add_conditions = ' _ '.join([str(du_row['media conditions']), str(du_row['electrolytes']), ''])
#         add_conditions = re.sub('_\s+_', '', add_conditions)
#         if master_pmg in empty:
#             master_file.at[master_index, 'Experimental conditions'] = add_conditions
#             print(master_index, '\t', 'new pmg', '\t', master_file.at[master_index, 'Experimental conditions'])
#         else:
#             master_file.at[master_index, 'Experimental conditions'] = ' _ '.join([str(master_pmg), str(add_conditions)]) 
#             print(master_index, '\t', 'new pmg', '\t', master_file.at[master_index, 'Experimental conditions'])  
                

        # match methods
        master_method = master_row['Method:']
        if self.scraping == 'noor':
            new_method = new_row['method']
        elif self.scraping == 'du':
            new_method = new_row['Method']
            
        if master_method == new_method:
            pass            
        elif master_method is nan or master_method  in empty:
            self.master_file.at[master_index, 'Method:'] = new_method
        elif new_method is not nan and new_method not in empty:
            new_methods = new_method.split(' and ')
            master_methods = new_method.split(' and ')
            combined_methods = set(new_methods + master_methods)

            if combined_methods is not None:
                combined_methods_string = ' and '.join([method for method in combined_methods])
            else:
                combined_methods_string = ' and '.join([new_method, master_method])

            self.master_file.at[master_index, 'Method:'] = combined_methods_string
            if verbose:
                print(master_index, '\t', 'new method', '\t', self.master_file.at[master_index, 'Method:'])

        # match EC values
        master_ec = master_row['EC Value:']
        if self.scraping == 'noor':
            new_ec = new_row['EC']
        elif self.scraping == 'du':
            new_ec = new_row['EC value']
            
        if master_ec is not nan and master_ec not in empty:
            master_ec = [master_ec]
            if master_ec[0] == new_ec:
                self.master_file.at[master_index, 'EC Value:'] = master_ec[0]   
            elif new_ec is not nan and new_ec not in empty:
                if re.search('&', new_ec):
                    new_ecs = new_ec.split('&')
                    #new_ecs = [str(ec) for ec in new_ecs]
                    total_ecs = unique(new_ecs + master_ec)
                else:
                    total_ecs = [master_ec[0], new_ec]
                self.master_file.at[master_index, 'EC Value:'] = " & ".join(total_ecs)
                if verbose:
                    print(master_index, '\t', 'new EC', '\t', self.master_file.at[master_index, 'EC Value:'])
        else:
            master_file.at[master_index, 'EC Value:'] = new_ec

        # match ionic strength concentrations
        master_ionic_strength = master_row['Ionic strength [mol / dm^3]']
        if self.scraping == 'noor':
            new_ionic_strength = new_row['ionic_strength']
        elif self.scraping == 'du':
            new_ionic_strength = new_row['Ionic strength']
        
        if str(master_ionic_strength) == str(new_ionic_strength):
            pass            
        elif master_ionic_strength is nan or master_ionic_strength  in empty:
            self.master_file.at[master_index, 'Ionic strength [mol / dm^3]'] = new_ionic_strength
        elif new_ionic_strength is not nan and new_ionic_strength not in empty:
            self.master_file.at[master_index, 'Ionic strength [mol / dm^3]'] = " & ".join([str(master_ionic_strength), str(new_ionic_strength)])
            if verbose:
                print(master_index, '\t', 'new ionic strength', '\t', self.master_file.at[master_index, 'Ionic strength [mol / dm^3]'])            

        # match the standard_id
        if master_row[f'{self.scraping}_index'] not in empty:
            print('proposed new index', new_index)
            print('--> ERROR: The master_index < {} > is predefined as < {} >.'.format(master_index, master_row[f'{self.scraping}_index']))
            self.master_file.loc[len(self.master_file.index)] = self.define_row(new_index, new_row, self.scraping)
        else:
            self.master_file.at[master_index, f'{self.scraping}_index'] = new_index
    
    # define the printing function
    def set_contrast(self, data_description, master_set, set_2, set_2_description, verbose = False, total_values = True):
        # print the original sets
        print('='*30)
        if total_values:
            print('\n{} in the master file: '.format(data_description), len(master_set))
            print('{} in the {}: '.format(data_description, set_2_description), len(set_2))

        # contrast the sets
        extra = master_set - set_2
        missing = set_2 - master_set
        if verbose:
            print('\nExtra {} in the master file, versus {}: '.format(data_description, set_2_description), len(extra_set_2), '\n', extra)
            print('\nMissing {} in the master file, versus {}: '.format(data_description, set_2_description), len(missing_set_2), '\n', missing)
        else:
            print('Extra {} in the master file, versus {}: '.format(data_description, set_2_description), len(extra))
            

            print('Missing {} in the master file, versus {}: '.format(data_description, set_2_description), len(missing))

        return missing

    def rounding(self, number):
        if self.scraping == 'noor':
            return float(number)
        elif self.scraping == 'du':
            return sci_notation(number, 2)