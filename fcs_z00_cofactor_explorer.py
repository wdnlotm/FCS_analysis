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

#add 'sample id; coloumns
def augmented_df(df, sid):
    df[('sample_id','sample_id')]=sid
    return df


## density plot grouped by sample id
def plot_density_grouped(ii, group_by, fcs_df_trimmed, cofactors, figure_dir, dataset_name):
    """ Function that plots marker expressiong density 
    plot grouped by sample_id for each marker with various cofactors"""
    # dataset_name='spect'
    bw_val=0.5
    frac_value=0.15
    alpha_val=0.5
    linewidth_val=1
    plt.rcParams['font.size'] = 8 # Set default font size
    num_col=5 #int(np.ceil(np.sqrt(fcs_df_trimmed.shape[1]-1)))
    num_row=int(np.ceil(len(cofactors)/num_col))
    fig, axes = plt.subplots(num_row, num_col, 
                         figsize=(2.0*num_col, 1.2*num_row) ) # 1 row, 2 columns
    marker = fcs_df_trimmed.columns[ii]

    for cf in cofactors:
        jj=cofactors.index(cf)
        row_index= jj//num_col
        col_index= jj%num_col
        
        fcs_df_trimmed_onemarker = fcs_df_trimmed[[marker, group_by]].copy()
        fcs_df_trimmed_onemarker = fcs_df_trimmed_onemarker.sample(frac=frac_value)
        fcs_df_trimmed_onemarker[marker] = np.arcsinh(fcs_df_trimmed_onemarker[marker]/cf)
        sns.kdeplot(data=fcs_df_trimmed_onemarker, x=marker, bw_adjust=bw_val, hue=group_by, 
            legend=False, ax=axes[row_index,col_index], alpha=alpha_val, linewidth=linewidth_val)
        axes[row_index,col_index].set_title(f"cofactor {cf}", fontsize=10)

    plt.tight_layout()
    filename=f'{dataset_name}_marker_{marker}_bw_{bw_val}_group_by_subjects.png'
    plt.savefig(f'{figure_dir}/{filename}')    
    plt.close('all')
    
    return filename


## density plot no groupping
def plot_density_nogroup_noglob(ii, fcs_df_trimmed, cofactors, figure_dir, dataset_name):
    """ Function that plots marker expressiong density 
    plot for each marker with various cofactors"""
    # dataset_name='spect'
    bw_val=0.5
    frac_value=0.15
    alpha_val=0.5
    linewidth_val=1
    plt.rcParams['font.size'] = 8 # Set default font size
    
    num_col=5 #int(np.ceil(np.sqrt(fcs_df_trimmed.shape[1]-1)))
    num_row=int(np.ceil(len(cofactors)/num_col))
    fig, axes = plt.subplots(num_row, num_col, 
                         figsize=(2.0*num_col, 1.2*num_row) ) # 1 row, 2 columns
    
    marker = fcs_df_trimmed.columns[ii]
    # print(marker)

    for cf in cofactors:
        jj=cofactors.index(cf)
        row_index= jj//num_col
        col_index= jj%num_col
        
        # print(fcs_df_trimmed.head(2))
        
        fcs_df_trimmed_onemarker = fcs_df_trimmed[[marker, 'sample_id']].copy()
        fcs_df_trimmed_onemarker = fcs_df_trimmed_onemarker.sample(frac=frac_value)
        fcs_df_trimmed_onemarker[marker] = np.arcsinh(fcs_df_trimmed_onemarker[marker]/cf)
        sns.kdeplot(data=fcs_df_trimmed_onemarker, x=marker, bw_adjust=bw_val, #hue='sample_id', 
            legend=False, ax=axes[row_index,col_index], alpha=alpha_val, linewidth=linewidth_val)
        axes[row_index,col_index].set_title(f"cofactor {cf}", fontsize=10)

    # print('I am here')
    plt.tight_layout()
    filename=f'{dataset_name}_marker_{marker}_bw_{bw_val}_no_group.png'
    # print(filename)
    
    # print(f'{figure_dir}/{filename}')
    plt.savefig(f'{figure_dir}/{filename}')    
    plt.close('all')
    
    return filename


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

    parser = argparse.ArgumentParser(description='high dimensional cytomery data z00 cofactor exploration')
    parser.add_argument('-uyml','--useyaml', type=bool, default=True, help='decide to use yaml or argparse')
    parser.add_argument('-conf','--config', type=str, default="config.yaml", help='configuration yaml file')
    parser.add_argument('-dl','--dataloc', type=str, default="../_Allcell/_subsample_100k_bcell/", help='data location')
    parser.add_argument('-fsd','--figuresavedir', type=str, default="figures_for_spectral_cofactor", help='figure save dir')
    parser.add_argument('-cfs','--cofactorlist', type=str, default="[1000.0, 2000.0, 3000.0]", help='cofactor list')
    parser.add_argument('-ds','--dataset', type=str, default="spectral", help='dataset name')
    parser.add_argument('-pbs','--plotbysubj', type=bool, default=False, help='True: will make density plot by subject')
    parser.add_argument('-np','--numpool', type=int, default=10, help='Number of cpu in nogroup plots')
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
            figure_dir = config['parameters']['z00']['figure_dir'] # figure_dir: where to save figures
            dataloc = config['parameters']['z00']['dataloc']       # data location
            cofactors = eval(config['parameters']['z00']['cofactorlist'])
            dataset_name = config['parameters']['z00']['dataset']
            plotbysubj = config['parameters']['z00']['plotbysubj']
            numpool =  config['parameters']['z00']['numpool']
            savefile_fcs_trimmed = config['parameters']['z00']['savefile_fcs_trimmed']
            
    print(config['parameters']['z00'])
    
  
    
    if not os.path.isdir(figure_dir):
        os.mkdir(figure_dir)
    

    samples_all = fk.load_samples(dataloc)
    
    sample_df_list=[augmented_df(samples_all[ii].as_dataframe(source='raw'), samples_all[ii].id) for ii in range(len(samples_all))]
    fcs_df=pd.concat(sample_df_list, axis=0)
    
    ###############################
    #### This data set specific task
    ###############################
    
    # Find coloumns to keep
    column_to_keep = len(fcs_df.columns)*[False]
    column_to_keep = [[fcs_df.columns[ii][1],(fcs_df.columns[ii][0]!=fcs_df.columns[ii][1]) ] for ii in range(len(fcs_df.columns))]
    
    # Add sample_id and remove viability
    column_to_keep[(list(zip(*column_to_keep))[0]).index('sample_id')][1]=True
    column_to_keep[(list(zip(*column_to_keep))[0]).index('Viability')][1]=False
    
    print(f'Columns to keep: {column_to_keep}')
    
    column_to_keep_index = [i for i, val in enumerate(  list(zip(*column_to_keep))[1]  ) if val == True]
    print(column_to_keep_index)
    # Find coloumns to keep - DONE
    
    
    marker_col = column_to_keep_index 
    fcs_df.columns[marker_col]

    col_orig=fcs_df.columns
    col_orig_list=list(col_orig)
    
    col_name_list2=[]
    # marker_col=[]
    
    for ii in range(len(col_orig_list)):
        rename=col_orig_list[ii][1].replace('-','')
        if col_orig_list[ii][1]=='CD127 (IL-7Ra)':
            rename='CD127'
        col_name_list2.append((col_orig_list[ii][0], rename))

    ###############################
    #### This data set specific task - DONE
    ###############################
    
    new_columns=pd.MultiIndex.from_arrays([[x[0] for x in col_name_list2],[y[1] for y in col_name_list2]], 
                              names=['pnn', 'pns'])
    
    new_columns_single = [x[1] for x in new_columns]
    new_columns_single
    fcs_df.columns=new_columns_single
    
    
    # global fcs_df_trimmed
    fcs_df_trimmed = fcs_df.iloc[:,marker_col]
    print(fcs_df_trimmed.head())
    
    fcs_df_trimmed.to_csv(savefile_fcs_trimmed, index=False, compression='gzip')

    # global num_markers
    num_markers=fcs_df_trimmed.shape[1]-1
    

    inputs = [(ii, fcs_df_trimmed, cofactors, figure_dir, dataset_name) for ii in range(num_markers)]
    
    with multiprocessing.get_context('spawn').Pool(numpool, initializer=init_pool, initargs=(results,)) as pool:
        list(tqdm(pool.imap_unordered(unpack_and_run, inputs), total=len(inputs)))


    if plotbysubj:
        inputs = [(ii, 'sample_id', fcs_df_trimmed, cofactors, figure_dir, dataset_name) for ii in range(num_markers)]
        # Somehow multiprocessing is slower than single processing. Keep 1 for the process count
        with multiprocessing.get_context('spawn').Pool(1, initializer=init_pool, initargs=(results,)) as pool:
            list(tqdm(pool.imap_unordered(unpack_and_run_group, inputs), total=len(inputs)))
