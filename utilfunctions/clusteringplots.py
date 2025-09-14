import sys, os, math, time
import subprocess

from random import sample

# import flowkit as fk
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
from numpy.polynomial import Polynomial

global color_list
file_to_execute = "./utilfunctions/color_list.py"
with open(file_to_execute, "r") as f: exec(f.read())


def run_cluster_umap(args):
    """Helper function to unpack arguments and call the main function."""
    return cluster_umap(*args)
    
#These two MUST be in the same file

def cluster_umap(fcs_df, rp, clustering_dir, label, groupby, figure_dir):
    plt.rcParams['font.size'] = 12
    image_scale = 3
    fig, axes = plt.subplots(1, 1, figsize=(5, 5))  # 1 row, 2 columns

    clustering=f'{clustering_dir}/rapids_leiden_{rp}_{label}.csv.gz'
    # clustering='rapids_leiden_rp_0.2_preserve.csv.gz'
    cluster_df=pd.read_csv(clustering, compression='gzip')

    df = pd.concat([fcs_df, cluster_df], axis=1)
   
    index_set=sorted(set(df[groupby]))

    sample_n = min( int(1e6), df.shape[0]  )
    df = df.sample(n=sample_n)

    fitcoeff = [0.15824382, -0.05592666,  0.00779626, -0.00035872] # found by curve fitting
    s_alpha = max(Polynomial(fitcoeff)(sample_n/1e5), 0.008)
    
    ai=0;  aj=0
    
    c_idx = 0
    for ii in index_set:#set(partition_df['partition']):
        im=axes.scatter(df.loc[df[groupby]==ii,'ux'], \
                    df.loc[df[groupby]==ii,'uy'], \
                    s = s_alpha, label = ii, c = color_list[c_idx], alpha = s_alpha)
        axes.set_title(f'{groupby}_rp = {rp}')
        c_idx = c_idx + 1

    # print(s_alpha)
    
    axes.axis('equal');
    legend = plt.legend(markerscale=0.8/s_alpha, bbox_to_anchor=(1.05, 1), loc='upper left')
    for handle in legend.legend_handles:
        # Set the alpha of the markers in the legend to 1.0 (fully opaque)
        handle.set_alpha(1.0)
    rp_str = str(rp)
    while len(rp_str) < 5:
        rp_str = rp_str + '0'
    
    plt.tight_layout()
    fig.savefig(f'{figure_dir}/rp{rp_str}_cluster_umap_{label}.png')
###############


##################################################

def run_overlapcheck(args):
    """Helper function to unpack arguments and call the main function."""
    return one_vs_others_umap(*args)

#These two MUST be in the same file
    
###########  One cluster vs others
def one_vs_others_umap(fcs_df, rp, clustering_dir, label, groupby, figure_dir):
    plt.rcParams['font.size'] = 12 # Set default font size
    image_scale = 5
    clustering=f'{clustering_dir}/rapids_leiden_{rp}_{label}.csv.gz'
    # clustering='rapids_leiden_rp_0.2_preserve.csv.gz'
    cluster_df=pd.read_csv(clustering, compression='gzip')

    df = pd.concat([fcs_df, cluster_df], axis=1)
    cluster_prop=df[groupby].value_counts()/df.shape[0]*100
    
    index_set=sorted(list(set(df[groupby])))
    
    sample_n = min( int(1e6), df.shape[0]  )
    df = df.sample(n=sample_n)
    
    fitcoeff = [0.15824382, -0.05592666,  0.00779626, -0.00035872] # found by curve fitting
    s_alpha = max(Polynomial(fitcoeff)(sample_n/1e5), 0.01)*2   
    
    subplot_y = math.ceil(len(index_set)*1.0/2)
    subplot_y = 2 if subplot_y == 1 else subplot_y
    fig, axes = plt.subplots(subplot_y, 2, 
                             figsize=(image_scale*2, image_scale*subplot_y))  # 1 row, 2 columns
    
    for partition_id in range(len(index_set)):
        # c_idx = 0
        for ii in index_set:
            aj=0 if partition_id<math.ceil(len(index_set)*1.0/2) else 1
            ai=partition_id%(math.ceil(len(index_set)*1.0/2)) 
            im=axes[ai,aj].scatter(df.loc[df[groupby]==ii,'ux'], \
                    df.loc[df[groupby]==ii,'uy'], \
                    s = s_alpha, label = ii, c = "red" if ii==index_set[partition_id] else "green", \
                                   alpha = s_alpha)
            axes[ai,aj].set_title(f'Partition {index_set[partition_id]}(red, {round(cluster_prop[index_set[partition_id]],2)}%) \nvs others (green)')
     
    if len(index_set)%2==1:
        axes[-1, -1].axis('off')
        
    rp_str = str(rp)
    while len(rp_str) < 5:
        rp_str = rp_str + '0'    
    
    plt.tight_layout()
    fig.savefig(f'{figure_dir}/rp{rp_str}_one_vs_others_{label}.png')


###############################

def run_clusterwisedensity(args):
    """Helper function to unpack arguments and call the main function."""
    return clusterwise_density_plot(*args)

#These two MUST be in the same file
    
################# density plots
def clusterwise_density_plot(fcs_df, type_markers, rp, clustering_dir, label, groupby, figure_dir):
    plt.rcParams['font.size'] = 14 # Set default font size
    image_scale = 3
    
    clustering=f'{clustering_dir}/rapids_leiden_{rp}_{label}.csv.gz'
    # clustering='rapids_leiden_rp_0.2_preserve.csv.gz'
    cluster_df=pd.read_csv(clustering, compression='gzip')

    df = pd.concat([fcs_df, cluster_df], axis=1)
    cluster_prop=df[groupby].value_counts()/df.shape[0]*100
    
    marker_max = df[type_markers].max()
    marker_min = df[type_markers].min()
    
    sample_n = min( int(2e6), df.shape[0]  )
    df = df.sample(n=sample_n)
    
    
    umap_fcs_data_by_clusters = df.groupby(groupby)
    
    # marker_max = fcs_data_type.max()
    # marker_min = fcs_data_type.min()
    # marker_max = fcs_data_type[type_markers].max()
    # marker_min = fcs_data_type[type_markers].min()
    
    cluster_list=list(umap_fcs_data_by_clusters.groups.keys())
    fig, axes = plt.subplots(len(cluster_list), len(type_markers), 
                             figsize=(image_scale*len(type_markers), image_scale*len(cluster_list) ))
    
    for p_idx in cluster_list:
        one_cluster = umap_fcs_data_by_clusters.get_group(p_idx)
        one_cluster=one_cluster[type_markers]
    
        midx=0
        pidx=cluster_list.index(p_idx)
        for m in type_markers:
            sns.kdeplot(data=one_cluster, x=m, ax=axes[pidx, midx])
            axes[pidx, midx].set(xlim=(marker_min[m], marker_max[m])) 
            axes[pidx, midx].set_title(f"Cluster {p_idx}, {round(cluster_prop[p_idx],2)}%", fontsize=12)
            midx+=1

    rp_str = str(rp)
    while len(rp_str) < 5:
        rp_str = rp_str + '0'    
    
    plt.tight_layout()
    fig.savefig(f'{figure_dir}/rp{rp_str}_marker_density_by_partition_{label}.png')

    
    # Display the plot
    