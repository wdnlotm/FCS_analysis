import os
import time
# import argparse
import subprocess

import sys
import yaml
import math
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

def init_pool(the_results):
  global results
  results = the_results

# for multiprocessing
def unpack_and_run_nogroup(args):
    """Helper function to unpack arguments and call the main function."""
    return plot_density_nogroup(*args)

def unpack_and_run_group(args):
    """Helper function to unpack arguments and call the main function."""
    return plot_density_grouped(*args)

## density plot no groupping
def plot_density_nogroup(m, fcs_df_trimmed, cofactors, figure_dir, dataset_name, **kwargs):
    """ Function that plots marker expressiong density 
    plot for each marker with various cofactors \n
    args:
    m - marker name
    fcs_df_trimmed - dataframe
    cofactors - cofactors to explorer
    figure_dir - figures will be saved here
    dataset_name - short description
    kwargs: 
    fraction = 0.15, default, #Subsampling fraction. 0 < x < 1 
    alpha = 0.5, default, #line transparency. 0 < a < 1. 
    font_size = 8 default, #integer for plt.rcParams['font.size'] 
    """
    
    bw_val=0.5
    frac_value=0.15
    if ('fraction' in kwargs.keys()):
        if (0 <= kwargs['fraction'])&(kwargs['fraction'] <= 1):
            frac_value = kwargs['fraction']
    alpha_val=0.5
    if ('alpha' in kwargs.keys()):
        if (0 <= kwargs['alpha'])&(kwargs['alpha'] <= 1):
            alpha_val = kwargs['alpha']
    linewidth_val=1
    plt.rcParams['font.size'] = 8 # Set default font size
    
    num_col=5 #int(np.ceil(np.sqrt(fcs_df_trimmed.shape[1]-1)))
    num_row=int(np.ceil(len(cofactors)/num_col))
    fig, axes = plt.subplots(num_row, num_col, 
                         figsize=(2.0*num_col, 1.2*num_row) ) # 1 row, 2 columns
    
    marker = m #fcs_df_trimmed.columns[ii]
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
