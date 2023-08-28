from os import listdir

import config
import sys
import warnings

from dataset.TPL import TplPionier
import dataset.preprocessing as dataset

import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
import random

 

sys.path.append('../../dataset-iop4230/')
config.append_paths()
if config.machine=='local':
    from dataset.TPL import TplPionier, TplGravity, TplMatisse
    import dataset.preprocessing as dataset
elif config.machine=='azure':
    from dataset.TPL import TplPionier, TplGravity, TplMatisse
    import dataset.preprocessing as dataset





    
############################## Camilo #########################################################
def proportion_pie_from_ds(ds,inst_title=None):
    fig, axes = plt.subplots(1, 3, figsize=(14,3))
    for i, flag in enumerate(['ERROR', 'TIMEOUT', 'Aborted']):
        error, not_error = 0, 0
        for value in ds.index[flag]:
            if value:
                error += 1
            else:
                not_error += 1
        labels=['{}\n{}'.format(flag,error), 'not {}\n{}'.format(flag,not_error)]
        axes[i].pie([error, not_error], labels=labels, colors=['tab:red','tab:blue'])
    if inst_title:
        plt.suptitle('Proportion of templates with anomalies for {}'.format(inst_title))
    else:
        plt.suptitle("Proportion of templates with anomalies for ds")
    plt.plot();

def proportion_pie(instrument,config=config.ds_small):
    "It plots the proportion of templates with the corresponding flag, for an instrument"
    if instrument=='Pionier':
        ds = TplPionier(config=config)
    elif instrument=='Gravity':
        ds = TplGravity(config=config)
    elif instrument=='Matisse':
        ds = TplMatisse(config=config)
    else:
        raise ValueError("instrument must match one of these strings: 'Pionier', 'Gravity', 'Matisse'")
    proportion_pie_from_ds(ds,inst_title=instrument)

def split_iterable(iterable,prop,shuffle=True):
    "shuffles and splits an iterable, needs random module"
    l = list(iterable)
    if shuffle:
        random.shuffle(l)
    cut = int(len(l)*prop)
    return l[:cut], l[cut:]

def split_subds(df,train_prop=.75):
    """ Splits sub-dataset into train and test indexes, attempting an even distribution across IDs

    Args:
        df (pandas DataFrame): sub-dataset
        train_prop (float, optional): default 0.75, percentage of indexes assigned to train set 

    Returns:
        train_indexes (list): indexes of train set
        test_indexes (list): indexes of test set
        
    """
    train_indexes, test_indexes = [], []
    for tpl_id in set(df['TPL_ID']):
        df_tpl = df[df['TPL_ID']==tpl_id]
        error_train, error_test = split_iterable(df_tpl[df_tpl['ERROR']==True].index,train_prop)
        success_train, success_test = split_iterable(df_tpl[df_tpl['ERROR']==False].index,train_prop)
        train_indexes += error_train + success_train
        test_indexes += error_test + success_test
    train_indexes = sorted(train_indexes)
    test_indexes = sorted(test_indexes)
    return train_indexes, test_indexes

def df_split(df,train_ind):
    """It returns a dataframe that appends the train-test split
        train_ind is a list of indexes and the column name will be 'split' """
    df_emb = df.copy()
    df_emb['split'] = ['train' if i in train_ind else 'test' for i in df.index]
    return df_emb


##########################################################################################################################

def generate_serie(obs, colorise): 
    firstrow=[];rows=[]
    for a in obs.load_trace(0)["event"]:
        firstrow.append(colorise.color(a))
        #borramos el espacio del comienzo y final
        firstrow=list(map(lambda x: x.strip(), firstrow))
        #hacemos el cambio para la primera fila:
        firstrow=list(map(lambda x: x.replace(' ','_'), firstrow))
        
    #and then we create the serie:
    serie= pd.Series([firstrow])
    
    #Finally we repeat this process to create the entire serie
    for i in range(1, len(obs.index)):
    
        for a in obs.load_trace(i)["event"]:
            rows.append(colorise.color(a))
            #borramos el espacio del comienzo y final de los demás
            rows=list(map(lambda x: x.strip(), rows))
            #Expandimos el cambio para el resto de la data
            rows=list(map(lambda x: x.replace(' ','_'), rows))
                
        serie=serie.append(pd.Series([rows],index=[i]))
        rows=[]
    
    return serie

def my_tokenizer(text):
    # split based on whitespace
    return re.split("\\s+",text)

def deleting_spaces(row):
    '''Replaces spaces with underscore
    
    Arg:
        row: (str). a specific event from a trace

    return:
        candidate (str): event without spaces
    '''
    
    candidate=row.strip()
    candidate=candidate.replace(' ','_')
    return candidate




