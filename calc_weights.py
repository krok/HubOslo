
import os
import sys
import pandas as pd
import json
import quantipy as qp


# CONFIG
data_dir = 'data'
if(len(sys.argv)==2):
    data_dir = sys.argv[1]
weights_filename = 'weights_def.json'
results_filename = 'results.json'
schema_filename = 'schema.json'
data_filename = 'data.json'

schema_file = os.path.join(data_dir, schema_filename)
data_file = os.path.join(data_dir,  data_filename)
weights_file = os.path.join(data_dir,  weights_filename)
results_file = os.path.join(data_dir,  'results', results_filename)

# READ DATA AND SCHEMA
dataset = qp.DataSet("test")
dataset.read_confirmit_from_files(schema_file, data_file)

# READ WEIGHTS DEF
with open(weights_file, "r") as weights_json:
    weights_def = json.load(weights_json)

# DEFINE WEIGHTS
scheme = qp.Rim('w')
group_targets = {}
for group_def in weights_def:    
    var_targets = []
    for target_def in group_def['targets']:        
        targets = dict()        
        for var_target_def in target_def['targets']:
            targets.update({var_target_def['code']:var_target_def['target']})
        var_target = dict()
        var_target[target_def['name']] = targets       
        var_targets.append(var_target)
    scheme.add_group(name=group_def['name'], filter_def=group_def['filter'], targets=var_targets)
    group_targets[group_def['name']] = group_def['target']

scheme.group_targets(group_targets)

# CALCUALTE WEIGHTS
dataset.weight(scheme, weight_name='weight', unique_key='responseid',inplace=True)

# WRITE WEIGHTS
weights = dataset.data().reindex(['responseid', 'weight'],axis='columns')
with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(weights.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
