"""
At this step z01, all relavant markers will be arcsinh transformed with the selected custom cofactors.
The transformed data will be prepared for the CyCombine batch correction. 
This dataframe will be saved as fcs_df_ready_for_cycombine.csv.gz and marker expression will be plotted as Pre_BC.
An R code will be called for CyCombine batch correction. The result would be saved as 
fcs_df_cycombine_BCed.csv.gz and Post BC plot will be generated.
"""
import os, sys, time, math

import argparse, yaml

import subprocess

from random import sample

import flowkit as fk
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import seaborn as sns

import multiprocessing
from itertools import starmap
from multiprocessing import Manager
from tqdm import tqdm

# global color_list 
# color_list = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8',\
#         '#f58231', '#911eb4', '#42d4f4', '#f032e6',\
#         '#bfef45', '#469990', '#dcbeff', '#9A6324',\
#         '#800000', '#808000', '#2f4f4f', '#a9a9a9',\
#         '#ffd8b1', '#000000', '#fffac8', '#aaffc3']

## in house
from utilfunctions import data_prep_for_cycombine, plot_markers_w_cf_by_batch

## Functions

def init_pool(the_results):
  global results
  results = the_results

## Functions - DONE

## Main - take inputs
##        1. figure_dir_name
##        2. data directory
##        3. cofactors
##        4. dataset name
##        5. True of False on plot density grouped by sample_id
##        6. number of pools for nogroup plot

if __name__ == "__main__":
    """Print this"""
    print(os.getcwd())

    manager = Manager()
    results = manager.list()

    parser = argparse.ArgumentParser(description='high dimensional cytomery data z01 batch correction')
    parser.add_argument('-uyml','--useyaml', type=bool, default=True, help='decide to use yaml or argparse')
    parser.add_argument('-conf','--config', type=str, default="config.yaml", help='configuration yaml file')
    parser.add_argument('-fcsdf','--fcstrimmed', type=str, default="fcs_df_trimmed.csv.gz", help='fcs df saved file')
    parser.add_argument('-cff','--cofactfile', type=str, default="cofactors.csv", help='cofactor file')
    parser.add_argument('-fsd','--figuresavedir', type=str, default="figures_for_batch_correct", help='figure save dir')
    # parser.add_argument('-cfs','--cofactorlist', type=str, default="[1000.0, 2000.0, 3000.0]", help='cofactor list')
    # parser.add_argument('-ds','--dataset', type=str, default="spectral", help='dataset name')
    # parser.add_argument('-pbs','--plotbysubj', type=bool, default=False, help='True: will make density plot by subject')
    # parser.add_argument('-np','--numpool', type=int, default=10, help='Number of cpu in nogroup plots')
    args, unknown = parser.parse_known_args()

    if not args.useyaml:
        figure_dir = args.figuresavedir #'figures_for_spectral_cofactor'
        dataloc = args.dataloc
        cofactors = eval(args.cofactorlist)  #[x*1000.0 for x in range(1,16)]+[20000.0, 30000.0]
        dataset_name = args.dataset
        plotbysubj = args.plotbysubj
        numpool = args.numpool

    if args.useyaml:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            figure_dir = config['z01']['figure_dir'] # figure_dir: where to save figures
            fcstrimmed = config['z01']['fcstrimmed']       # data location
            cofactorfile = config['z01']['cofactorfile']
            numpool =  config['z01']['numpool']
            batchinfo = config['z01']['batchinfo']

    print(config['z01'])


    if not os.path.isdir(figure_dir):
        os.mkdir(figure_dir)

    start_time = time.perf_counter()
    fcs_df_trimmed = pd.read_csv(fcstrimmed, compression='gzip')
    duration = time.perf_counter() - start_time
    print(f"Computation time: {duration:.4f} seconds")    
    
    cofactor_df=pd.read_csv(cofactorfile)
    cofactor_df = cofactor_df.sort_values(by='class')
    type_markers = list(cofactor_df['antigen'][cofactor_df['class']=="clustering"])
    markers = list(cofactor_df['antigen'])
    
    with open("markers_to_batchcorrect.csv", "w") as file:
        for item in markers:
            file.write(item + "\n")

    print(fcs_df_trimmed.head(3))
    print(cofactor_df)
    print(f'clustering markers: {type_markers}')
    print(f'all markers: {markers}')
    
    fcs_df_trimmed = fcs_df_trimmed[list(cofactor_df['antigen'])+['sample_id']]
    print(fcs_df_trimmed.head())

    cofactor_series = pd.Series(list(cofactor_df['cofactor']), index=cofactor_df['antigen'])
    print(cofactor_series)

    # fcs_df_trimmed
    fcs_df_trimmed_transformed_w_custom_cf = fcs_df_trimmed.div(cofactor_series, axis=1)
    fcs_df_trimmed_transformed_w_custom_cf['sample_id'] = fcs_df_trimmed['sample_id'].copy()

    print('Divided by cofactors but before arcsinh transform')
    print(fcs_df_trimmed_transformed_w_custom_cf.head())

    fcs_df_trimmed_transformed_w_custom_cf[ list(cofactor_df['antigen']) ]= \
    np.arcsinh(fcs_df_trimmed_transformed_w_custom_cf[ list(cofactor_df['antigen']) ].values)
    
    print('After arcsinh transformation')
    print(fcs_df_trimmed_transformed_w_custom_cf.head())
  
    fcs_df_trimmed_transformed_w_custom_cf = \
    data_prep_for_cycombine(fcs_df_trimmed_transformed_w_custom_cf, 'VEH')

    batch_info = pd.read_csv(batchinfo)
    batch_info['file_name']=batch_info['file_name'].map(lambda x: int(x.replace(".fcs","")))
    print(batch_info.head())

    message = f"""The batch information will be add by modifying sample_id. An example of 'sample_id' is {fcs_df_trimmed_transformed_w_custom_cf['sample_id'][0]}. We need to decide the string that needs to be ignored."""
    print(message)
    replace_this_str = input('String to be ignored: ')

    batch_mapping = dict(zip(list(batch_info['file_name']), list(batch_info['batch'])))
    fcs_df_trimmed_transformed_w_custom_cf['batch'] = \
    (fcs_df_trimmed_transformed_w_custom_cf['sample_id'].copy()).map(lambda x: int(x.replace(replace_this_str,"")) )
    fcs_df_trimmed_transformed_w_custom_cf['batch'] = \
    fcs_df_trimmed_transformed_w_custom_cf['batch'].map(batch_mapping)

    print(fcs_df_trimmed_transformed_w_custom_cf['batch'].value_counts())

    print(fcs_df_trimmed_transformed_w_custom_cf.head())
    
    print(f"Pre BC plots")
    savefilename=f'Pre_batch_correction_markers_w_custom_cofactor_nogroup.png'
    plot_markers_w_cf_by_batch(fcs_df_trimmed_transformed_w_custom_cf, cofactor_df, figure_dir, savefilename)

    
    start_time = time.perf_counter()
    fcs_df_trimmed_transformed_w_custom_cf.to_csv("fcs_df_ready_for_cycombine.csv.gz", index=False, compression='gzip')
    duration = time.perf_counter() - start_time
    print(f"Computation time: {duration:.4f} seconds")
    
    print(f"Starting CyCombine...")
    start_time = time.perf_counter()

    cycombine_commands = """module load apptainer; SIF=/project/iprime_storage/myles_kim/imageD/R441_cytof/rstudio_R443_v6.sif; 
    apptainer exec $SIF Rscript fcs_z01_cyCombine_simple.r fcs_df_ready_for_cycombine.csv.gz markers_to_batchcorrect.csv fcs_df_cycombine_BCed.csv.gz"""

    try:
        # Execute the command using the system shell
        result = subprocess.run(
            cycombine_commands, 
            shell=True, 
            check=True, 
            text=True, 
            capture_output=True
        )

        # Print the command's standard output
        print("Standard Output:\n", result.stdout)
        
        # Print any standard error messages
        print("Standard Error:\n", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}")
        print("Error output:\n", e.stderr)
    
    duration = time.perf_counter() - start_time
    print(f"CyCombine Computation time: {duration:.4f} seconds")

    print(f"Saving BCed fcs data...")
    fcs_df_BCed = pd.read_csv('fcs_df_cycombine_BCed.csv.gz', compression='gzip')

    print(f"Post BC plot...")
    savefilename=f'Post_batch_correction_markers_w_custom_cofactor_nogroup.png'
    plot_markers_w_cf_by_batch(fcs_df_BCed, cofactor_df, figure_dir, savefilename)
 


    
