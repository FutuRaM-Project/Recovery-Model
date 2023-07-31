"""
object_import_export.py

This is a script to export and import the model and other model objects to file. Export formats are:

- JSON
- pickle

Methods:

- export(model_object, filename, format='pickle'):  

    Wrapper function to export the model object to file.

- export_to_json(model_, filename)

- export_to_pickle(model, filename)

- import(filename)

Dependencies:

- pickle
- json
- datetime
- os

#! this has not yet been fully tested. it could be that the model object is not fully exported to json and then imported again. the pickel export and import seems to work fine though. maybe we need to make a function to convert the model object to a fully to a dictionary first.

"""

import os
import json
import pickle
from datetime import datetime


def import_object(filename):
    '''
    This is a function to import a model object from file.

    Usage example:

    TestModel_ELV = import('TestModel_ELV-20230707-1620.pkl')
    '''

    if not os.path.isfile(filename):
        print(f'File not found: {filename}')
        model_object = None

    else:
        try:
            if filename.endswith('.json'):
                model_object = pickle.load(open(filename, 'rb'))

            if filename.endswith('.pkl'):
                model_object = pickle.load(open(filename, 'rb'))

        except Exception as e:
            print(f'Error loading file {filename}: {e}')

    return model_object


def export_object(model_object, filename=None, file_format='pickle'):
    """
    This is a wrapper function to export the model object to file.

    """
    EXPORT_DIR = '../export/'
    if not os.path.isdir(EXPORT_DIR):
        os.mkdir(EXPORT_DIR)

    if filename is None:

        filename = f'{model_object.name}-{datetime.now().strftime("%Y%m%d_%H%M")}'

    filename = os.path.join(EXPORT_DIR, filename)

    if file_format == 'pickle':
        filename = filename + '.pkl'
        export_to_pickle(model_object, filename)

    elif file_format == 'json':
        filename = filename + '.json'
        export_to_json(model_object, filename)

    else:
        print('File format not supported. Please choose either "pickle" or "json".')


#! TODO: make this function, maybe we need to make a function to convert the model object to a fully to a dictionary first.
def export_to_json(model_object, filename):
    '''
    Exports the model object to a JSON file.

    Parameters
    ----------
    model_object :
        The model object to export. (can be a model,process, flow, or matter object)
    filename : str
        The filename to export the model object to.
        without the .json extension.

    Default filename is the object name and the current date and time. Default location is the export folder.
    '''

    model_json = model_object.to_json()

    try:

        json.dump(model_json, open(filename, 'w'))
        print(f'\n\n{"="*90}\n\t Exported model object to file: {filename}\n{"="*90}\n')

    except Exception as e:
        print(f'Error exporting model object to file: {e}')


def export_to_pickle(model_object, filename):
    '''
    Exports the model object to a pickle file.

    Parameters
    ----------
    model_object :
        The model object to export. (can be a model,process, flow, or matter object)
    filename : str
        The filename to export the model object to.
        without the .pkl extension.

    Default filename is the object name and the current date and time. Default location is the export folder.

    '''

    try:

        pickle.dump(model_object, open(filename, 'wb'))
        print(f'\n\n{"="*90}\n\t Exported model object to file: {filename}\n{"="*90}\n')

    except Exception as e:
        print(f'Error exporting model object to file: {e}')


