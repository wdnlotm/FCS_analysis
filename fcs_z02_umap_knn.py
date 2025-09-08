import os
import time
import argparse
import subprocess
# import bokeh
# from bokeh.plotting import show

import sys
import yaml

import umap

import math
from random import sample

import flowkit as fk
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

global color_list 
color_list = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8',\
        '#f58231', '#911eb4', '#42d4f4', '#f032e6',\
        '#bfef45', '#469990', '#dcbeff', '#9A6324',\
        '#800000', '#808000', '#2f4f4f', '#a9a9a9',\
        '#ffd8b1', '#000000', '#fffac8', '#aaffc3']

## Functions

def init_pool(the_results):
  global results
  results = the_results


def unpack_and_run(args):
    """Helper function to unpack arguments and call the main function."""
    return plot_density_nogroup_noglob(*args)

def unpack_and_run_group(args):
    """Helper function to unpack arguments and call the main function."""
    return plot_density_grouped(*args)


def edgelist_by_umap(fcs_data, type_markers, label):
    
    print("Calculating KNN")
    print(fcs_data[type_markers].head(3))
    
    start_time = time.perf_counter()
    knn_UMAP=umap.umap_.nearest_neighbors(fcs_data[type_markers],  n_neighbors=16, metric='euclidean', 
                             metric_kwds=None, angular=False, random_state=1)
    duration = time.perf_counter() - start_time
    print(f"knn computation time: {duration:.4f} seconds")  
    
    indices=pd.DataFrame(knn_UMAP[0])
    indices_wo_self = indices.iloc[:,1:indices.shape[1]]
    
    indices_wo_self.shape
    
    edgelist=pd.DataFrame({'src':np.repeat(  range(indices_wo_self.shape[0]), indices_wo_self.shape[1]  )}, dtype="int32")
    edgelist['dst']=indices_wo_self.values.reshape(indices_wo_self.shape[0]*indices_wo_self.shape[1], order='C')
    print(f'edgelist shape: {edgelist.shape}')
    
    edgelist.to_csv(f"edgelist_{label}.csv.gz", index=False, compression="gzip")
    duration = time.perf_counter() - start_time
    print(f"knn compute and save time: {duration:.4f} seconds")

    return f"edgelist_{label}.csv.gz"

# def umap_calculation(fcs_data, type_markers):
#     start_time = time.perf_counter()
    
#     reducer = umap.UMAP(min_dist=0.01, n_neighbors=15)
#     embedding = reducer.fit_transform(fcs_data[type_markers])
#     umap_df = pd.DataFrame({'ux':embedding[:,0], 'uy':embedding[:,1]})
#     umap_df.to_csv(f"umap_df_{len(type_markers)}markers.csv.gz", compression="gzip", index=False)
    
#     duration = time.perf_counter() - start_time
#     print(f"umap computing time: {duration:.4f} seconds")  

#     return f"umap_df_{len(type_markers)}markers.csv.gz"

def umap_calculation(fcs_data, type_markers, queue):
    pid = os.getpid()
    print(f"[PID: {pid}] Starting task with input: ")
    start_time = time.perf_counter()
    
    reducer = umap.UMAP(min_dist=0.01, n_neighbors=15)
    embedding = reducer.fit_transform(fcs_data[type_markers])
    umap_df = pd.DataFrame({'ux':embedding[:,0], 'uy':embedding[:,1]})
    umap_df.to_csv(f"umap_df_{len(type_markers)}markers.csv.gz", compression="gzip", index=False)
    
    duration = time.perf_counter() - start_time
    print(f"umap computing time: {duration:.4f} seconds")  
    
    queue.put(("umap_file", f"umap_df_{len(type_markers)}markers.csv.gz"))

def umap_density_plot(fcs_df, figure_dir, label):
    sample_n = n=min(int(1e6), fcs_df.shape[0])
    s_alpha = 0.025
    if sample_n < 6e5:
        s_alpha = 0.03
    
    umap_df_sample = fcs_df[['ux','uy']].sample(n=sample_n)
    
    plt.scatter(umap_df_sample['ux'], umap_df_sample['uy'], s=s_alpha, alpha = s_alpha, c = "blue");
    plt.axis('equal');
    plt.savefig(f'{figure_dir}/umap_density_{label}.png')

def umap_marker_plot(fcs_df, type_markers, figure_dir, label):
    plt.rcParams['font.size'] = 9 # Set default font size
    image_scale=3
    sample_n = n=min(int(2e5), fcs_df.shape[0])
    umap_fcs_data_sample = fcs_df[type_markers + ['ux','uy']].sample(n=sample_n)

    fig, axes = plt.subplots(math.ceil(len(type_markers)*1.0/2), 2, 
                             figsize=(image_scale*2, image_scale*math.ceil(len(type_markers)*1.0/2)))  # 1 row, 2 columns

    msize=0.005
    malpha=0.99

    for midx in range(len(type_markers)):
        m=type_markers[midx]
        aj=0 if midx < math.ceil(len(type_markers)*1.0/2) else 1
        ai=midx%(math.ceil(len(type_markers)*1.0/2)) 
        im=axes[ai,aj].scatter(umap_fcs_data_sample['ux'], umap_fcs_data_sample['uy'], 
                               c=umap_fcs_data_sample[m],
                               s=msize, alpha = malpha, cmap = 'jet');
        # plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)#, pad=0.04)
        # Create the colorbar
        cb = plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)
        
        # Set the colorbar's alpha to 1.0 (fully opaque)
        cb.mappable.set_alpha(0.05)
        
        axes[ai,aj].set_title(f'{m}')
        axes[ai,aj].axis('equal');
    if len(type_markers)%2==1:
        axes[-1, -1].axis('off')

    plt.tight_layout()
    plt.savefig(f'{figure_dir}/umap_markers_{label}.png')
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

    parser = argparse.ArgumentParser(description='high dimensional cytomery data z01 batch correction')
    parser.add_argument('-fcsdf','--fcsdata', type=str, default="fcs_df_cycombine_BCed.csv.gz", help='fcs data file')
    parser.add_argument('-cff','--cofactfile', type=str, default="cofactors.csv", help='cofactor file')
    parser.add_argument('-fsd','--figuresavedir', type=str, default="figures_for_spectral_umap", help='figure save dir')
    # parser.add_argument('-cfs','--cofactorlist', type=str, default="[1000.0, 2000.0, 3000.0]", help='cofactor list')
    # parser.add_argument('-ds','--dataset', type=str, default="spectral", help='dataset name')
    # parser.add_argument('-pbs','--plotbysubj', type=bool, default=False, help='True: will make density plot by subject')
    # parser.add_argument('-np','--numpool', type=int, default=10, help='Number of cpu in nogroup plots')
    args, unknown = parser.parse_known_args()

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        label = config['parameters']['z02']['label']
    
    figure_dir = args.figuresavedir #'figures_for_spectral_cofactor'
    if not os.path.isdir(figure_dir):
        os.mkdir(figure_dir)
    
    manager = Manager()
    results = manager.list()

    start_time = time.perf_counter()
    fcs_data=pd.read_csv(args.fcsdata, compression='gzip')#, index_col=0)
    duration = time.perf_counter() - start_time
    print(f"Computation time: {duration:.4f} seconds")
    print(fcs_data.head(3))
 
    cofactor_df=pd.read_csv(args.cofactfile)
    cofactor_df = cofactor_df.sort_values(by='class')
    type_markers = list(cofactor_df['antigen'][cofactor_df['class']=="clustering"])
    markers = list(cofactor_df['antigen'])

    print(f'type markers: {type_markers}')
    print(f'all markers: {markers}')

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        label = config['parameters']['z02']['label']
        
    print(label)
    
    # edgelist_by_umap(fcs_data, type_markers, label)
    # umap_calculation(fcs_data, type_markers)
    result_queue = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=edgelist_by_umap, args=(fcs_data, type_markers, label))

    # Keyword arguments are passed using 'kwargs'
    p2 = multiprocessing.Process(target=umap_calculation, args=(fcs_data, type_markers, result_queue))
    
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

    umap_density_plot(fcs_data_umap, figure_dir, label)
    umap_marker_plot(fcs_data_umap, type_markers, figure_dir, label)