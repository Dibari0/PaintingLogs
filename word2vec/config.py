import sys
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def detect_machine():
    if os.path.exists('../../../../data/raw'):
        return 'azure'
    elif os.path.exists('../../sm2022-dataset-tpl/data/raw'):
        return 'local'
    else:
        raise ModuleNotFoundError("No paranal instruments data detected")

def append_paths(verbose=False):
    if machine=='local':
        sys.path.insert(1, '../../dataset-iop4230/')
        sys.path.append('../../parlogan')
        sys.path.append('../../sm2022-dataset-tpl')
        if verbose:
            print("successfully added parlogan and dataset paths, local machine")
    elif machine=='azure':
        sys.path.insert(1, '../../../../dataset-iop4230/')
        sys.path.append('../../../../parlogan/')
        sys.path.append('../../../../sm2022-dataset-tpl')
        if verbose:
            print("successfully added parlogan and dataset paths, azure machine")


machine = detect_machine()
append_paths()


dataset_dir = 'sm2022-dataset-tpl/data'
processed_dir = f'{dataset_dir}/processed'

dsDir_small = '../../sm2022-dataset-tpl/data/raw' if machine=='local' else '../../../../sm2022-dataset-tpl/data/raw'
ds_small = {
    'startTimestamp': '2021-01-01T00:00:00.000',
    'stopTimestamp':  '2021-01-02T00:00:00.000',
    'dataset_dir':dsDir_small,
    'processed_dir': dsDir_small.replace('/raw','/processed')
}

# ds_medium available on both azure and local, although in different directories
dsDir_medium = '../../sm2022-dataset-tpl/data/raw' if machine=='local' else '../../../../data/raw'
ds_medium = {
    'startTimestamp': '2020-12-01T00:00:00.000',
    'stopTimestamp':  '2021-01-02T00:00:00.000',
    'dataset_dir': dsDir_medium,
    'processed_dir': dsDir_medium.replace('/raw','/processed')
}

# ds_big only available in azure
ds_big = {
    'startTimestamp': '2020-10-01T00:00:00.000',
    'stopTimestamp':  '2021-04-01T00:00:00.000',
    'dataset_dir': '../../../../data/raw',
    'processed_dir': '../../../../data/processed'
}
