import os
import time
# import argparse
import subprocess
# import bokeh
# from bokeh.plotting import show

import sys
import yaml

import umap

import math
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
## density plot no groupping
def plot_density_nogroup(m, fcs_df_trimmed, cofactors, figure_dir, dataset_name, **kwarg):
    """ Function that plots marker expressiong density 
    plot for each marker with various cofactors \n
    kwargs: \n
    fraction = x, #Subsampling fraction. 0 < x < 1 \n
    alpha = a, #line transparency. 0 < a < 1. \n
    font_size = 10, #integer"""
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
