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

master_file = pandas.read_csv('2021-09-04_master_TECR_2.csv')
# combine the ionic strength columns
for index, value in master_file[['Ionic strength [mol / dm^3]', 'Ionic strength [mol / kg]']].iterrows():
    if value['Ionic strength [mol / kg]'] in empty:
        master_file.at[index, 'Ionic strength [mol / kg]'] = value['Ionic strength [mol / dm^3]']
    elif value['Ionic strength [mol / kg]'] not in empty:
        if value['Ionic strength [mol / dm^3]'] not in empty:
            if value['Ionic strength [mol / dm^3]'] != value['Ionic strength [mol / kg]']:
                print(value['Ionic strength [mol / dm^3]'], '\t', value['Ionic strength [mol / kg]'])
                master_file.at[index, 'Ionic strength [mol / kg]'] = average(value['Ionic strength [mol / kg]'], value['Ionic strength [mol / dm^3]'])

for index, row in master_file.iterrows():
    # open a new JSON template
    json_template = json.load(open('template.json'))
    # define components of the JSON
    for key, value in json_template.items():
        if key == 'curator':
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
            
#             print(row['Reaction:'])
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
                
                value['representative_reaction']['stoichiometry']['reactants'] = reactants_dict
                value['representative_reaction']['stoichiometry']['products'] = products_dict
            
            # define the measurement data
            value['equilibriumConstant'] = row['Keq']
            value['hydrogenPotential'] = row['pH ']
            value['temperature'] = row['T [K]']
            value['ionicStrength'] = row['Ionic strength [mol / kg]']
            pmg = re.search('(\d+.?\d+) = -log\[Mg\+2\]', row['Experimental conditions'])
            if pmg is not None:
                value['magnesiumPotential'] = pmg.group()
                
                
            # define comments
            
    # export the datum JSON
    os.mkdir('./datum_points')
    count = 0
    ec = row['EC Value:']
    reference = re.sub('(/)', '-', row['Reference ID:'])
    export_name = '_'.join([reference, ec, str(count)])
    while os.path.exists(f'./datum_points/{export_name}.json'):
        count += 1
        export_name = '_'.join([reference, ec, str(count)])
    
    with open(f'./datum_points/{export_name}.json', 'w') as out:
        json.dump(json_template, out, indent = 4)