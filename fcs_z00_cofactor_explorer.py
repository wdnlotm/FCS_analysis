import os, sys, time, math

import argparse, yaml

from random import sample

import flowkit as fk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import seaborn as sns

import subprocess
import multiprocessing
from itertools import starmap
from multiprocessing import Manager

from tqdm import tqdm

## in-house
from utilfunctions import init_pool, unpack_and_run_nogroup, plot_density_nogroup

global color_list 
color_list = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8',\
        '#f58231', '#911eb4', '#42d4f4', '#f032e6',\
        '#bfef45', '#469990', '#dcbeff', '#9A6324',\
        '#800000', '#808000', '#2f4f4f', '#a9a9a9',\
        '#ffd8b1', '#000000', '#fffac8', '#aaffc3']
## Functions

#add 'sample id; coloumns
def augmented_df(df, sid):
    df[('sample_id','sample_id')]=sid
    return df

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

    # parser = argparse.ArgumentParser(description='high dimensional cytomery data z00 cofactor exploration')
    # parser.add_argument('-uyml','--useyaml', type=bool, default=True, help='decide to use yaml or argparse')
    # parser.add_argument('-conf','--config', type=str, default="config.yaml", help='configuration yaml file')
    # parser.add_argument('-dl','--dataloc', type=str, default="../_Allcell/_subsample_100k_bcell/", help='data location')
    # parser.add_argument('-fsd','--figuresavedir', type=str, default="figures_for_spectral_cofactor", help='figure save dir')
    # parser.add_argument('-cfs','--cofactorlist', type=str, default="[1000.0, 2000.0, 3000.0]", help='cofactor list')
    # parser.add_argument('-ds','--dataset', type=str, default="spectral", help='dataset name')
    # parser.add_argument('-pbs','--plotbysubj', type=bool, default=False, help='True: will make density plot by subject')
    # parser.add_argument('-np','--numpool', type=int, default=10, help='Number of cpu in nogroup plots')
    # args, unknown = parser.parse_known_args()
    
    # if not args.useyaml:
    #     figure_dir = args.figuresavedir #'figures_for_spectral_cofactor'
    #     dataloc = args.dataloc
    #     cofactors = eval(args.cofactorlist)  #[x*1000.0 for x in range(1,16)]+[20000.0, 30000.0]
    #     dataset_name = args.dataset
    #     plotbysubj = args.plotbysubj
    #     numpool = args.numpool

    
    # if args.useyaml:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        figure_dir = config['z00']['figure_dir'] # figure_dir: where to save figures
        dataloc = config['z00']['dataloc']       # data location
        cofactors = eval(config['z00']['cofactorlist'])
        dataset_name = config['z00']['dataset']
        plotbysubj = config['z00']['plotbysubj']
        numpool =  config['z00']['numpool']
        savefile_fcs_trimmed = config['z00']['savefile_fcs_trimmed']
            
    print(config['z00'])

    os.makedirs(f'{figure_dir}', exist_ok=True)

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
    
    print(f'Saving trimmed fcs data: {savefile_fcs_trimmed}')
    fcs_df_trimmed.to_csv(savefile_fcs_trimmed, index=False, compression='gzip')

    print(f'Saving trimmed fcs data done!!!')
    
    global num_markers
    num_markers=fcs_df_trimmed.shape[1]-1
    marker_list = fcs_df_trimmed.columns[0:num_markers]
    print(marker_list)
    print(len(marker_list))
    
    print(f'Making plots')
    inputs = [(m, fcs_df_trimmed, cofactors, figure_dir, dataset_name) for m in marker_list]
    
    with multiprocessing.get_context('spawn').Pool(numpool, initializer=init_pool, initargs=(results,)) as pool:
        list(tqdm(pool.imap_unordered(unpack_and_run_nogroup, inputs), total=len(inputs)))

