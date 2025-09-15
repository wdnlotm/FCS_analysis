"""
Need to run this with RAPIDS container
apptainer exec --nv $RAPIDS_SIF python fcs_spect_z03_RAPIDS_leiden.py
"""
import os
import yaml
import sys
import cudf
import cupy
import cugraph
import pandas as pd
from datetime import datetime

if __name__ == "__main__":
    print(os.getcwd())
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        outputdir = config['all']['outputdir']
        inputfiles = config['all']['inputfiles']
        label = config['z03']['label']
        rp_list = eval(config['z03']['rp_list'])
        save_dir = outputdir + '/' + config['z03']['save_dir']
    print(f'resolution parameter list: {rp_list}')
 
    
    big_cluster_thres = 0.5 # [PERCENT]
    
    edgelist_file = outputdir + '/' + f'edgelist_{label}.csv.gz'
    edges = cudf.read_csv(edgelist_file, dtype=['int32', 'int32'], compression="gzip")
    
    G=cugraph.MultiGraph(directed=False)
    G.from_cudf_edgelist(edges, source="src", destination="dst", renumber = False) 

    del edges

    os.makedirs(save_dir, exist_ok=True)
        
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime("%H_%M_%S")
    print_file = f'{save_dir}/print_output_{formatted_time}.txt'
    
    pof = open(print_file, 'w')
    print(f'Printout for leiden clustering: {label}', file=pof, flush=True)

    rseed=1234
    
    for rp in rp_list:
        time1 = datetime.now()
        print(time1, file=pof, flush=True)
        parts, modularity_score = cugraph.leiden(G, max_iter=100, resolution = rp, random_state=rseed)
        time2 = datetime.now()
        print(time2, file=pof, flush=True)
        print(time2-time1, file=pof, flush=True)
        
        
        partition = parts.to_pandas()
        count = partition['partition'].value_counts()
        proportion = count*100/partition.shape[0]  # [PERCENT]
        bigenough=proportion[proportion > big_cluster_thres]
        result_tuple = ('computation time = ' + str(time2-time1), \
                'resolution =  ' + str(rp), \
                'random_state =  ignore this ' + str(123), \
                # 'number of cluster = ' + str(parts.partition.max()+1), \
                'number of cluster = ' + str(proportion.shape[0]), \
                'modularity score = ' + str(modularity_score), \
                'big enough clusters (>' + str(big_cluster_thres) + '%) = ' + str(bigenough.shape[0]), \
                'big enough cluster total = ' + str(bigenough.sum()), \
                bigenough, \
                proportion) 
        
        
        print(result_tuple[0:2], file=pof, flush=True)
        print(result_tuple[3:7], file=pof, flush=True)
        print(result_tuple[8], file=pof, flush=True)
        print('###################################################', file=pof, flush=True)
    
        partition.to_csv(f'{save_dir}/rapids_leiden_{rp}_{label}.csv.gz', index=False, compression="gzip")
    
    pof.close()
