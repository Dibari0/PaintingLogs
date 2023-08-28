from os import listdir

import config
import sys
import warnings

from dataset.TPL import TplPionier
import dataset.preprocessing as dataset

import matplotlib.pyplot as plt
import pandas as pd
import re
import random
import os
import pickle
from datetime import datetime
import glob

 

sys.path.append('../../dataset-iop4230/')
config.append_paths()
if config.machine=='local':
    from dataset.TPL import TplPionier, TplGravity, TplMatisse
    import dataset.preprocessing as dataset
elif config.machine=='azure':
    from dataset.TPL import TplPionier, TplGravity, TplMatisse
    import dataset.preprocessing as dataset

    
############################## Camilo functions #########################################################
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

def proportion_pie_from_ds_v2(ds,inst_title=None):
    fig, axes = plt.subplots(1, 3, figsize=(14,3))
    for i, flag in enumerate(['ERROR', 'TIMEOUT', 'Aborted']):
        error, not_error = 0, 0
        for value in ds[flag]:
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

def load_topic_list(num_topics=None, file=None):
    '''Load the specified file using two different ways:
        (1) the exact file name
        (2) the number of topics used to create the saved list. For this case, the newest saved file is loaded.
    input:
        num_topics: [int] N of topics used to create the saved list.
        file: [string] Name of the saved file.
    return:
        topics: [list] newest/specified topics-per-log list.
    '''

    if num_topics:
        # Load the last file with the number of topics specified
        files = os.listdir("TopicsPerLog")
        matching_files = [f for f in files if re.match(fr"TPL_{num_topics}_\d{{8}}_\(\d+\)\.pk", f)]
        if matching_files:
            #Files loaded and sorted according to date and version
            latest_file = max(matching_files, key=lambda f: (re.search(fr"\d{{8}}", f).group(0), int(re.search(r'\((\d+)\)', f).group(1))))
            with open(f"TopicsPerLog/{latest_file}", "rb") as f:
                topics = pickle.load(f)
            print(f"List with topics-per-log loaded from TopicsPerLog/{latest_file}")
            return topics
        else:
            print(f" Pickle file with {num_topics} topics not found")
            return None
    
    if file:
        # Load the spicifed file
        try:
            with open(f"TopicsPerLog/{file}", "rb") as f:
                topics = pickle.load(f)
            print(f"List with topics-per-log loaded from TopicsPerLog/{file}")
            return topics
        except FileNotFoundError:
            print(f"{file} not found")
            return None
    
    # name file and number of topics not specified
    print("You must specify the file name or a number of topics to load the corresponding list of topics")
    return None


def save_topic_list(topics,n_topics):
    '''Save the list topics in a pickle file using n_topics, datetime and version as ID.
    input:
        topics: [list] Nested list that contains the predominant topic for each log.
        n_topics: [int] Number of topics used to obtain the list topics.
    '''
    
    # Naming the pickle file
    timestamp = datetime.now().strftime("%d%m%Y")
    filename = f"TopicsPerLog/TPL_{n_topics}_{timestamp}_(0).pkl"
    
    # If it already exists a file with the same name, a suffix is added
    version = 1
    while os.path.exists(filename):
        filename = f"TopicsPerLog/TPL_{n_topics}_{timestamp}_({version}).pkl"
        version += 1
    
    # Saving the list in the pickle file
    try:
        with open(filename, "wb") as f:
            pickle.dump(topics, f)
        print(f"{filename} saved successfully")
    except:
        print("Oh oh, something happened with the saving")

def save_corpus_to_pickle(corpus, instrument, size):
    '''This function saves the corpus created before as a pickle file which name has: name of the insturment, 
       size of the dataset and version, as a ID. 
    input:
        corpus: [dataframe] Corpus to be stored.
        instrument: [str] Name of the instrument which the dataset comes from.
        size: [str] Size of the Dataset. It can be: small or medium
    '''
    # Create Corpus Folder if it doesnt' exist
    if not os.path.exists("Corpus"):
        os.makedirs("Corpus")
    
    # naming the pickle file
    now = datetime.now().strftime("%d%m%Y")
    version = 1
    filename = f"Corpus/{instrument}_{size}_{now}_v{version}.pkl"
    
    # If the file already exists, we increase its version
    while os.path.exists(filename):
        version += 1
        filename = f"Corpus/{instrument}_{size}_{now}_v{version}.pkl"
    
    # Saving the dataframe as a pickle file
    with open(filename, "wb") as f:
        pickle.dump(corpus, f)
    
    print(f"The file: {filename} has been saved successfully.")

def load_corpus(instrument=None, size=None, filename=None):
    ''' Load the corpus spicified in two different ways: giving the specific name or both instrument and size.
        Using the second way, the last file created will always be loaded 
    input:
        instrument: [str] Name of the instrument which the dataset comes from.
        size: [str] Size of the Dataset (small or medium).
        filename: [str] specific name of the file to be loaded.
    return:
        corpus: [dataframe] corpus created before.'''

    if filename:
        corpus = pd.read_pickle('Corpus/'+ filename)
        print(f"Loaded file: {filename}")
        return corpus
    
    if instrument is not None and size is not None:
        pattern = f"Corpus/{instrument}_{size}_*.pkl"
        files = glob.glob(pattern)
        if not files:
            print(f"No files found with pattern: {pattern}")
            return None

        # Sort files by date and version
        files.sort(key=lambda x: (re.findall(r"\d{8}", x), re.findall(r"_(\d+)\.pkl", x)))
        file_to_load = files[-1]

        corpus = pd.read_pickle(file_to_load)
        print(f"Loaded file: {file_to_load}")
        return corpus
    
    print("Please provide either filename or both instrument and size.")
    return None

def graphic_pertrace(data=TplPionier(config=config.ds_medium).index, corpus=load_corpus( instrument='Pionier', size='medium'), trace= int, topics= int):
    
    #define traces with error and non error
    error_indexes=list(data[data['ERROR'] == True].index)
    if trace in error_indexes:
        trace_index = error_indexes[trace]
        #Error_label
        error_label='True'
    else:
        non_error_indexes=list(data[data['ERROR'] == False].index)
        trace_index=non_error_indexes[trace]
        error_label='False'

    #import the specific tokens for the trace given
    trace_logs = corpus.tokens.iloc[trace_index]

    #import the topics per log for the trace given
    topics_pertrace= load_topic_list(num_topics=topics)
    if not topics_pertrace:
        return None 

    trace_topics = topics_pertrace[trace_index]

    #graph settings:
    num_logs = len(trace_logs)
    fig, ax = plt.subplots(figsize=(25, 5))
    for i in range(num_logs):
        topic = trace_topics[i]
        log = trace_logs[i]
        color = f'C{topic}'
        ax.bar(i, 1, color=color, edgecolor='black')
        ax.text(i, 0.5,f' {topic}', ha='center', va='center',fontsize=10)
    ax.set_xlim([-0.5, num_logs-0.5])
    ax.set_ylim([0, 1])
    ax.set_xlabel('Log')
    ax.set_ylabel('Tópico')
    ax.set_title(f'Tópicos para la traza {trace_index}. Cantidad de logs {num_logs}. ERROR: {error_label}, LDA {topics} topics')
    plt.show()




