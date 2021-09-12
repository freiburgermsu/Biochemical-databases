from numpy import nan
import pandas
import json
import os
import re

empty = [nan, None, ' ', '']

def average(num_1, num_2):
    numbers = num_1.split(' & ')
    numbers.extend(num_2.split(' & '))
    numbers = set([float(num.strip()) for num in numbers])
    summation = sum(list(numbers))
    average = summation / len(numbers)
    return average


class master_to_json():
    def __init__(self, master_file, json_template):
        self.master_file = master_file
        self.template = json_template
        
    def parse_to_json(self, curator = 'APF', export = True):
        for index, row in self.master_file.iterrows():
            # define components of the JSON
            for key, value in self.template.items():
                if key == 'curator':
                    if curator == 'APF':
                        value['orcid'] = 'https://orcid.org/0000-0002-7288-535X'
                        value['name'] = 'Andrew Philip Freiburger' 
                elif key == 'CuratedMeasurement':
                    # define the reference content
                    value['reference']['pmid'] = row['PMID']
                    value['reference']['doi'] = row['DOI']
                    value['reference']['tecrdb_string'] = row['Reference:']
                    value['reference']['tecrdb_id'] = row['Reference ID:']

                    # define the reaction 
                    value['representative_reaction']['name'] = row['Enzyme:']
                    value['representative_reaction']['KEGG'] = row['KEGG Reaction:']
                    value['representative_reaction']['CID'] = row['CID Reaction:']

                    if type(row['Reaction:']) is str:
                        if not re.search('=', row['Reaction:']):
                            value['representative_reaction']['stoichiometry'] = row['Reaction:']
                        else:
                            reactants, products = row['Reaction:'].split('=')
                            reactants = reactants.split(' + ')
                            reactants_dict = {}
                            for reactant in reactants:
                                coef = re.search('\d\s', reactant)
                                if coef is None:
                                    coef = 1
                                else:
                                    coef = coef.group()
                                reactants_dict[reactant] = coef

                            products = products.split(' + ')
                            products_dict = {}
                            for product in products:
                                coef = re.search('\d\s', product)
                                if coef is None:
                                    coef = 1
                                else:
                                    coef = coef.group()
                                products_dict[product] = coef

                            if type(value['representative_reaction']['stoichiometry']) is not str:
                                value['representative_reaction']['stoichiometry']['reactants'] = reactants_dict
                                value['representative_reaction']['stoichiometry']['products'] = products_dict
                    else:
                        print('--> ERROR: The {} reaction of master_index {} is unexpected.'.format(row['Reaction:'], index))

                    # define the measurement data
                    value['equilibriumConstant'] = row['Keq']
                    value['hydrogenPotential'] = row['pH ']
                    value['temperature'] = row['T [K]']
                    value['ionicStrength'] = row['Ionic strength [mol / kg]']
                    pmg = re.search('(\d+.?\d+) = -log\[Mg\+2\]', str(row['Experimental conditions']))
                    if pmg is not None:
                        value['magnesiumPotential'] = pmg.group()
                    # define comments

            # export the datum JSON
            if not os.path.exists('./datum_points'):
                os.mkdir('./datum_points')
            count = 0
            ec = row['EC Value:']
            if type(row['Reference ID:']) is str:
                reference = re.sub('(/)', '-', row['Reference ID:'])
            else:
                print('--> ERROR: The {} reference ID of master_index {} is unexpected.'.format(row['Reaction:'], index))
                reference = ''
            export_name = '_'.join([reference, str(ec), str(count)])
            while os.path.exists(f'./datum_points/{export_name}.json'):
                count += 1
                export_name = '_'.join([reference, str(ec), str(count)])
            
            if export:
                with open(f'./datum_points/{export_name}.json', 'w') as out:
                    json.dump(self.template, out, indent = 4)