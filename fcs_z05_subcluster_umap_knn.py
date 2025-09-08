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

def separate_clusters(fcs_data, cluster_df, figure_dir, rp_pick):
    if fcs_data.shape[0]==cluster_df.shape[0]:
        fcs_data['partition']=cluster_df['partition'].values
    
    for cl in list(fcs_data['partition'].unique()):
        save_cluster_filename = f'{figure_dir}/cluster_{cl}_rp_pick{rp_pick}_fcs_data_umap.csv.gz'
        print(f'Cluster {cl} saved. The size of dataframe is')
        print((fcs_data.loc[fcs_data['partition']==cl,:]).shape)
        (fcs_data.loc[fcs_data['partition']==cl,:]).to_csv(save_cluster_filename, compression='gzip')

def edgelist_by_umap_clusterwise(fcs_data, type_markers, figure_dir, cl):
    
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

    savefile_name = f"{figure_dir}/edgelist_cluster_{cl}.csv.gz"
    
    edgelist.to_csv(savefile_name, index=False, compression="gzip")
    duration = time.perf_counter() - start_time
    print(f"knn compute and save time: {duration:.4f} seconds")

    return savefile_name

def umap_calculation_clusterwise(fcs_data, type_markers, figure_dir, cl, min_dist, queue):
    pid = os.getpid()
    print(f"[PID: {pid}] Starting task with input: ")
    start_time = time.perf_counter()
    
    reducer = umap.UMAP(min_dist=min_dist, n_neighbors=15)
    embedding = reducer.fit_transform(fcs_data[type_markers])
    umap_df = pd.DataFrame({'ux':embedding[:,0], 'uy':embedding[:,1]})
    
    savefile_name = f'{figure_dir}/umap_df_cluster_{cl}_{len(type_markers)}markers.csv.gz'
    umap_df.to_csv(savefile_name, compression="gzip", index=False)
    
    duration = time.perf_counter() - start_time
    print(f"umap computing time: {duration:.4f} seconds")  
    
    queue.put(("umap_file", savefile_name))

def umap_density_plot_onecl(fcs_df, figure_dir, cl):
    sample_n = n=min(int(1e6), fcs_df.shape[0])
    s_alpha = 0.025
    if sample_n < 6e5:
        s_alpha = 0.2
    
    umap_df_sample = fcs_df[['ux','uy']].sample(n=sample_n)
    
    plt.scatter(umap_df_sample['ux'], umap_df_sample['uy'], s=s_alpha, alpha = s_alpha, c = "blue");
    plt.axis('equal');
    plt.tight_layout()
    plt.savefig(f'{figure_dir}/umap_density_cluster_{cl}.png')
    plt.clf()

def umap_marker_plot_onecl(fcs_df, type_markers, figure_dir, cl):
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
                               s=msize, alpha = malpha, cmap = 'jet', vmin = marker_min[m], vmax=marker_max[m]);
        # plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)#, pad=0.04)
        # Create the colorbar
        cb = plt.colorbar(im, ax=axes[ai,aj], fraction=0.046)
        
        # Set the colorbar's alpha to 1.0 (fully opaque)
        cb.mappable.set_alpha(0.1)
        
        axes[ai,aj].set_title(f'{m}')
        axes[ai,aj].axis('equal');
    if len(type_markers)%2==1:
        axes[-1, -1].axis('off')

    plt.tight_layout()
    plt.savefig(f'{figure_dir}/umap_markers_cluster_{cl}.png')
    plt.clf()
## Functions - DONE

if __name__ == "__main__":
    print(os.getcwd())
    
    manager = Manager()
    results = manager.list()
    
    parser = argparse.ArgumentParser(description='high dimensional cytomery data z01 batch correction')
    parser.add_argument('-uyml','--useyaml', type=bool, default=True, help='decide to use yaml or argparse')
    parser.add_argument('-conf','--config', type=str, default="config.yaml", help='configuration yaml file')
    
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
            rp_pick = config['z05']['rp_pick'] 
            figure_dir = config['z05']['figure_dir']
            figure_dir = f'{figure_dir}_rp_pick{rp_pick}' # figure_dir: where to save figures
            cofactorfile = config['z05']['cofactorfile']
            label =  config['z05']['label']
            fcs_umap_savedfile = config['z05']['fcs_umap_saved']
            min_dist = config['z05']['min_dist']

    if not os.path.isdir(figure_dir):
        os.mkdir(figure_dir)

    fcs_data=pd.read_csv(fcs_umap_savedfile, compression='gzip')#, index_col=0)
    print(fcs_data.head())
    
    cofactor_df=pd.read_csv(cofactorfile)
    cofactor_df = cofactor_df.sort_values(by='class')
    type_markers = list(cofactor_df['antigen'][cofactor_df['class']=="clustering"])
    markers = list(cofactor_df['antigen'])

    print(type_markers)
    
    marker_max = fcs_data[type_markers].max()
    marker_min = fcs_data[type_markers].min()

    rp = rp_pick

    clustering_dir=f'partition_{label}'
    clustering=f'{clustering_dir}/rapids_leiden_{rp}_{label}.csv.gz'
    cluster_df=pd.read_csv(clustering, compression='gzip')
    print(cluster_df['partition'].value_counts()/cluster_df.shape[0])

    separate_clusters(fcs_data, cluster_df, figure_dir, rp_pick)

    cluster_list = list(cluster_df['partition'].unique())
    print(cluster_list)

    del fcs_data, cluster_df

    for cl in cluster_list:
        saved_cluster_filename = f'{figure_dir}/cluster_{cl}_rp_pick{rp_pick}_fcs_data_umap.csv.gz'
        fcs_data_onecl = pd.read_csv(saved_cluster_filename, compression='gzip')#, index_col=0)
        fcs_data_onecl = fcs_data_onecl.drop(columns = ['ux','uy'])
        print(fcs_data_onecl.head())
        
        result_queue = multiprocessing.Queue()
                         
        p1 = multiprocessing.Process(target=edgelist_by_umap_clusterwise, args=(fcs_data_onecl, type_markers, figure_dir, cl))
    
        # Keyword arguments are passed using 'kwargs'
        p2 = multiprocessing.Process(target=umap_calculation_clusterwise, \
                                     args=(fcs_data_onecl, type_markers, figure_dir, cl, min_dist, result_queue))
    
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
    
        umap_df_onecl = pd.read_csv(output_umap[1], compression='gzip')
        
        fcs_data_umap_onecl = pd.concat([fcs_data_onecl, umap_df_onecl], axis=1)
        
        print(fcs_data_umap_onecl.columns)
        print(fcs_data_umap_onecl.head())
    
        # umap_density_plot_onecl(fcs_data_umap_onecl, figure_dir, cl)
        # umap_marker_plot_onecl(fcs_data_umap_onecl, type_markers, figure_dir, cl)


    