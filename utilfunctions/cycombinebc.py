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


global color_list
file_to_execute = "./utilfunctions/color_list.py"
with open(file_to_execute, "r") as f: exec(f.read())
# color_list = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8',\
#         '#f58231', '#911eb4', '#42d4f4', '#f032e6',\
#         '#bfef45', '#469990', '#dcbeff', '#9A6324',\
#         '#800000', '#808000', '#2f4f4f', '#a9a9a9',\
#         '#ffd8b1', '#000000', '#fffac8', '#aaffc3']


def data_prep_for_cycombine(df, condition, **kwargs):
    """ 
    Function that add necessary columns to dataframe to setup for CyCombine \n
    args:
    df - fcs dataframe
    condition = 'VEH' or others. One condition.
    kwargs:
    condition_list - more than one condition. must have df.shape[0]==len(condition_list)
    """
    df_return = df
    num_cells = df_return.shape[0]
    df_return = pd.concat([pd.DataFrame({'id':list(range( num_cells ))}), df_return], axis=1)
    # add 'sample'
    df_return['sample'] = (df_return['sample_id'].copy()).map(lambda x: x.replace(".fcs","") )
    # add 'condition'
    df_return['condition'] = condition
    if ('condition_list' in kwargs.keys()):
        if (len(kwargs['condition_list']) == df.shape[0]):
            df_return['condition'] = kwargs['condition_list']
    # add temporary 'batch'
    df_return['batch']=100 #temporary number info
    return df_return



def plot_markers_w_cf_by_batch(fcs_df, cofactor_df, figure_dir, filename, **kwargs):
    """ 
    Function that plots marker expression density with the chosen cofactors separated by batch \n
    args:
    fcs_df - fcs dataframe with batch information ['batch']
    cofactor_df - cofactor_df['antigen']: markers, cofactor_df['cofactor']: cofactors
    figure_dir, filename - figure saving location and name
    kwargs:
    condition_list - more than one condition. must have df.shape[0]==len(condition_list)
    """
    bw_val=0.5
    frac_value=0.1
    alpha_val=0.5
    linewidth_val=1
    plt.rcParams['font.size'] = 8 # Set default font size

    num_markers=cofactor_df.shape[0]
    antigen = list(cofactor_df['antigen'])
    num_col=5 #int(np.ceil(np.sqrt(fcs_df_trimmed.shape[1]-1)))
    
    num_row=int(np.ceil(( num_markers )/num_col))
    fig, axes = plt.subplots(num_row, num_col, 
                             figsize=(2.0*num_col, 1.2*num_row) ) # 1 row, 2 columns
    # print(fcs_df_trimmed.head())
    # num_markers=fcs_df_trimmed_transformed_w_custom_cf.shape[1]-1
    
    num_batch=len(set(fcs_df['batch']))
    for ii in range(num_markers):
        row_index= ii//num_col
        col_index= ii%num_col
    
        marker = antigen[ii]  #fcs_df_trimmed_transformed_w_custom_cf.columns[ii]
    
        cf = cofactor_df['cofactor'][cofactor_df['antigen']==marker].values
        cf = cf[0]*1.0
        marker_class = cofactor_df['class'][cofactor_df['antigen']==marker].values[0]
    
        sns.kdeplot(data=fcs_df, x=marker,bw_adjust=bw_val, hue='batch', palette=color_list[0:num_batch],
                ax=axes[row_index,col_index], alpha=alpha_val, linewidth=linewidth_val, legend=False)
        if ii==num_markers-1:
            sns.kdeplot(data=fcs_df, x=marker,bw_adjust=bw_val, hue='batch', palette=color_list[0:num_batch],
                        ax=axes[row_index,col_index], alpha=alpha_val, linewidth=linewidth_val, legend=True)
        axes[row_index,col_index].set_title(f"cf {cf} {marker_class[0:5]}", fontsize=10)
    
    
    plt.tight_layout()
    
    plt.savefig(f'{figure_dir}/{filename}')   
    plt.close('all')

