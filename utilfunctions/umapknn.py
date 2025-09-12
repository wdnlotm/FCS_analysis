import os, sys, time, math
import subprocess
# import bokeh
# from bokeh.plotting import show

from random import sample

import umap
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import seaborn as sns

import multiprocessing
from itertools import starmap
from multiprocessing import Manager
from tqdm import tqdm
from numpy.polynomial import Polynomial
## Functions

def init_pool(the_results):
  global results
  results = the_results


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

def umap_density_plot(fcs_df, figure_dir, label, **kwargs):
    plt.rcParams['font.size'] = 11
    fig, axes = plt.subplots(1, 1, figsize=(5, 5))  # 1 row, 2 columns
    sample_n = n=min(int(1e6), fcs_df.shape[0])
    fitcoeff = [0.15824382, -0.05592666,  0.00779626, -0.00035872] # found by curve fitting
    s_alpha = max(Polynomial(fitcoeff)(sample_n/1e5), 0.005)
    
    umap_df_sample = fcs_df[['ux','uy']].sample(n=sample_n)
    
    plt.scatter(umap_df_sample['ux'], umap_df_sample['uy'], s=s_alpha, alpha = s_alpha, c = "blue");
    plt.axis('equal');
    plt.savefig(f'{figure_dir}/umap_density_{label}.png')

def umap_marker_plot(fcs_df, type_markers, marker_min, marker_max, figure_dir, label, **kwargs):
    plt.rcParams['font.size'] = 11 # Set default font size
    image_scale=5 #3
    sample_n = n=min(int(2e5), fcs_df.shape[0])

    fitcoeff = [0.15824382, -0.05592666,  0.00779626, -0.00035872] # found by curve fitting
    s_alpha = max(Polynomial(fitcoeff)(sample_n/1e5)*1, 0.009)
                                             ## Due to image_scale=3 x 2
    umap_fcs_data_sample = fcs_df[type_markers + ['ux','uy']].sample(n=sample_n)

    fig, axes = plt.subplots(math.ceil(len(type_markers)*1.0/2), 2, 
                             figsize=(image_scale*2, image_scale*math.ceil(len(type_markers)*1.0/2)))  # 1 row, 2 columns


    for midx in range(len(type_markers)):
        m=type_markers[midx]
        aj=0 if midx < math.ceil(len(type_markers)*1.0/2) else 1
        ai=midx%(math.ceil(len(type_markers)*1.0/2)) 
        im=axes[ai,aj].scatter(umap_fcs_data_sample['ux'], umap_fcs_data_sample['uy'], 
                               c=umap_fcs_data_sample[m], s=s_alpha, alpha = 0.9, cmap = 'jet',
                              vmin = marker_min[m] , vmax = marker_max[m]);
        # plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)#, pad=0.04)
        # Create the colorbar
        cb = plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)
        
        # Set the colorbar's alpha to 1.0 (fully opaque)
        cb.mappable.set_alpha(s_alpha)
        
        axes[ai,aj].set_title(f'{m}')
        axes[ai,aj].axis('equal');
    if len(type_markers)%2==1:
        axes[-1, -1].axis('off')

    plt.tight_layout()
    plt.savefig(f'{figure_dir}/umap_markers_{label}.png')
