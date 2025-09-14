"""
At this step z02, 
the edgelist of 15-NN graph will be calculated.
The umap projection coordinates will be calculated.
They will run in parallel to save time. umap calculate takes longer.
This step also saves markers global max and min.
"""
import os, sys, time, math
import argparse, yaml
import subprocess
# import bokeh
# from bokeh.plotting import show

from random import sample

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import seaborn as sns

import multiprocessing
from itertools import starmap
from multiprocessing import Manager
from tqdm import tqdm

# in-house
sys.path.insert(0, './')
from utilfunctions import edgelist_by_umap, umap_calculation, umap_density_plot, umap_marker_plot

## Functions

def init_pool(the_results):
  global results
  results = the_results


if __name__ == "__main__":
    print(os.getcwd())

    # parser = argparse.ArgumentParser(description='high dimensional cytomery data z01 batch correction')
    # parser.add_argument('-fcsdf','--fcsdata', type=str, default="fcs_df_cycombine_BCed.csv.gz", help='fcs data file')
    # parser.add_argument('-cff','--cofactfile', type=str, default="cofactors.csv", help='cofactor file')
    # parser.add_argument('-fsd','--figuresavedir', type=str, default="figures_for_spectral_umap", help='figure save dir')
    # # parser.add_argument('-cfs','--cofactorlist', type=str, default="[1000.0, 2000.0, 3000.0]", help='cofactor list')
    # # parser.add_argument('-ds','--dataset', type=str, default="spectral", help='dataset name')
    # # parser.add_argument('-pbs','--plotbysubj', type=bool, default=False, help='True: will make density plot by subject')
    # # parser.add_argument('-np','--numpool', type=int, default=10, help='Number of cpu in nogroup plots')
    # args, unknown = parser.parse_known_args()

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        outputdir = config['all']['outputdir']
        inputfiles = config['all']['inputfiles']
        figure_dir = outputdir + '/' + config['z02']['figure_dir'] # figure_dir: where to save figures
        fcsdata_BCed = outputdir + '/' + config['z02']['fcsdata']       # data location
        cofactorfile = inputfiles + '/' + config['z02']['cofactorfile']
        label =  config['z02']['label']
        min_distance = config['z02']['min_distance']
        fcs_umap_savefile = outputdir + '/' + config['z02']['fcs_umap_savefile']
            
    os.makedirs(figure_dir, exist_ok=True)
    
    manager = Manager()
    results = manager.list()

    start_time = time.perf_counter()
    fcs_data=pd.read_csv(fcsdata_BCed, compression='gzip')#, index_col=0)
    duration = time.perf_counter() - start_time
    print(f"Computation time: {duration:.4f} seconds")
    print(fcs_data.head(3))
 
    cofactor_df=pd.read_csv(cofactorfile)
    cofactor_df = cofactor_df.sort_values(by='class')
    type_markers = list(cofactor_df['antigen'][cofactor_df['class']=="clustering"])
    markers = list(cofactor_df['antigen'])

    marker_max = fcs_data[markers].max()
    marker_max.to_csv(f'{outputdir}/marker_max_BCed.csv')
    marker_min = fcs_data[markers].min()
    marker_min.to_csv(f'{outputdir}/marker_min_BCed.csv')
  
    print(f'type markers: {type_markers}')
    print(f'all markers: {markers}')

    
    # edgelist_by_umap(fcs_data, type_markers, label)
    # umap_calculation(fcs_data, type_markers)
    result_queue = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=edgelist_by_umap, args=(fcs_data, type_markers, label, outputdir))

    # Keyword arguments are passed using 'kwargs'
    p2 = multiprocessing.Process(target=umap_calculation, args=(fcs_data, type_markers, outputdir, result_queue))
    
    start_time = time.perf_counter()
    p1.start()
    p2.start()

    # Wait for both processes to complete
    p1.join()
    p2.join()
    
    duration = time.perf_counter() - start_time
    print(f"multiprocessing computing time: {duration:.4f} seconds")    
    output_umap = result_queue.get()
    print(f'{output_umap[0]}:{output_umap[1]}')

    umap_df = pd.read_csv(output_umap[1], compression='gzip')
    fcs_data_umap = pd.concat([fcs_data, umap_df], axis=1)
    print(fcs_data_umap.columns)
    print(fcs_data_umap.head())
    fcs_data_umap.to_csv('fcs_data_umap.csv.gz', index=False, compression='gzip')

    marker_max = fcs_data_umap[type_markers].max()
    marker_min = fcs_data_umap[type_markers].min()  

    umap_density_plot(fcs_data_umap, figure_dir, label)
    umap_marker_plot(fcs_data_umap, type_markers, marker_min, marker_max, figure_dir, label)
