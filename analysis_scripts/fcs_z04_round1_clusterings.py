"""
At this step z04, cluster results are visualized.
1. Cluster UMAPs
2. Check cluster overlaps
3. Clusterwise marker expression density
"""

import os, time, sys, math

import subprocess
import yaml
from random import sample

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import seaborn as sns

import multiprocessing
import multiprocess
from itertools import starmap

from multiprocessing import Manager

from tqdm import tqdm

# in-house
sys.path.insert(0, './')
from utilfunctions import init_pool, cluster_umap, one_vs_others_umap, clusterwise_density_plot
from utilfunctions import run_cluster_umap, run_overlapcheck, run_clusterwisedensity

# global color_list 
# color_list = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8',\
#         '#f58231', '#911eb4', '#42d4f4', '#f032e6',\
#         '#bfef45', '#469990', '#dcbeff', '#9A6324',\
#         '#800000', '#808000', '#2f4f4f', '#a9a9a9',\
#         '#ffd8b1', '#000000', '#fffac8', '#aaffc3']

## Functions

# def init_pool(the_results):
#   global results
#   results = the_results




# def unpack_and_run2(args):
#     """Helper function to unpack arguments and call the main function."""
#     return one_vs_others_umap(*args)

# def unpack_and_run3(args):
#     """Helper function to unpack arguments and call the main function."""
#     return density_plot(*args)




## Functions - DONE

## Main - take inputs
##        1. figure_dir_name
##        2. data directory
##        3. cofactors
##        4. dataset name
##        5. True of False on plot density grouped by sample_id
##        6. number of pools for nogroup plot

if __name__ == "__main__":
    print(os.getcwd())
    manager = Manager()
    results = manager.list()

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        outputdir = config['all']['outputdir']
        inputfiles = config['all']['inputfiles']
        figure_dir = outputdir + '/' + config['z04']['figure_dir']
        label = config['z04']['label']
        cofactorfile = inputfiles + '/' + config['z04']['cofactorfile']
        rp_list = eval(config['z04']['rp_list'])
        fcs_umap_savefile = outputdir + '/' + config['z04']['fcs_umap_savefile']
        load_dir = outputdir + '/' + config['z04']['load_dir']

    print(config['z04'])

    os.makedirs(figure_dir, exist_ok=True)

    clustering_dir=f'{load_dir}'
    
    cofactor_df=pd.read_csv(cofactorfile)
    cofactor_df = cofactor_df.sort_values(by='class')
    type_markers = list(cofactor_df['antigen'][cofactor_df['class']=="clustering"])

    fcs_df = pd.read_csv(fcs_umap_savefile, compression='gzip')
    print(fcs_df.head())

    
    inputs = [(fcs_df, rp, clustering_dir, label, 'partition', figure_dir) for rp in rp_list]  
    with multiprocessing.get_context('spawn').Pool(4, initializer=init_pool, initargs=(results,)) as pool:
        list(tqdm(pool.imap_unordered(run_cluster_umap, inputs), total=len(inputs)))
    
    inputs = [(fcs_df, rp, clustering_dir, label, 'partition', figure_dir) for rp in rp_list]
    
    with multiprocessing.get_context('spawn').Pool(4, initializer=init_pool, initargs=(results,)) as pool:
        list(tqdm(pool.imap_unordered(run_overlapcheck, inputs), total=len(inputs)))

    inputs = [(fcs_df, type_markers, rp, clustering_dir, label, 'partition', figure_dir) for rp in rp_list]
    
    with multiprocessing.get_context('spawn').Pool(4, initializer=init_pool, initargs=(results,)) as pool:
        list(tqdm(pool.imap_unordered(run_clusterwisedensity, inputs), total=len(inputs)))