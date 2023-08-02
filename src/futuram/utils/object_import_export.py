"""
object_import_export.py

This is a script to export and import the model and other model objects to file. 

Export formats are:

- JSON
- pickle

#! this has not yet been fully tested. it could be that the model object is not fully exported to json and then imported again. the pickel export and import seems to work fine though. maybe we need to make a function to convert the model object to a fully to a dictionary first.

"""

import os
import json
import pickle
from datetime import datetime


def import_object(filename=None):
    """
    This is a function to import a model object from file.
    If there is no filename specified, it will import the latest file from the export folder.

    Parameters
    ----------
    filename : str

        The filename to import the model object from.

        Default filename is the object name and the date and time of export. Default location is the export folder.

    Usage example
    -------------

    TestModel_ELV = import('TestModel_ELV-20230707-1620.pkl')

    """

    if filename is None:
        export_dir = "../export/"
        files = os.listdir(export_dir)

        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(export_dir, f)), reverse=True)

        file_times = {}

        print(f'\n\n{"="*90}\n\t Importing model object from latest file in export folder: {export_dir}\n{"="*90}\n')
        print(f'{"-"*90}\n\t Other files in export folder are:')
        print(*files, sep='\n', end=f'\n{"-"*90}\n')
        
    else: 
        files = [filename]
        export_dir = ''
        # for file in files:
        #     file_path = os.path.join(export_dir, file)
        #     file_times[file] = os.path.getmtime(file_path)

        #     # Find the file with the latest modification time
        #     latest_file = max(file_times, key=file_times.get)

    model_object = None
    for file in files:
        file = os.path.join(export_dir, file)
        try:
            if file.endswith(".json"):
                model_object = json.load(open(file, "rb"))

            if file.endswith(".pkl"):
                model_object = pickle.load(open(file, "rb"))

            print(
                f'\n\n{"="*90}\n\t Imported model object "{model_object.name}" from file: {file}\n{"="*90}\n')
            break  # Stop iterating over files if import was successful

        except Exception as e:
            print(f"\t **** Error loading file {file}: {e}")

    if model_object is None:
        print("*"*90)
        print(f"\t No valid files found in {export_dir}")
        print("*"*90)

    return model_object


def export_object(model_object, filename=None, file_format="pickle"):
    """
    This is a wrapper function to export the model object to file.

    """
    export_dir = "../export/"
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

    if filename is None:
        filename = f'{model_object.name}-{datetime.now().strftime("%Y%m%d_%H%M_%S")}'

    filename = os.path.join(export_dir, filename)

    if file_format == "pickle":
        filename = filename + ".pkl"
            
        try:
            export_to_pickle(model_object, filename)
        except Exception as e:
            print(f'{"*90"}\n Error exporting model object to file: \n{e}"{"*"*90}')
            os.remove(filename)

    elif file_format == "json":
        filename = filename + ".json"

        try:
            export_to_json(model_object, filename)
        except Exception as e:
            print(f'{"*90"}\n Error exporting model object to file: \n{e}"{"*"*90}')
            os.remove(filename)

#! TODO: make this function, maybe we need to make a function to convert the model object to a fully to a dictionary first.


def export_to_json(model_object, filename):
    """
    Exports the model object to a JSON file.

    Parameters
    ----------
    model_object :
        The model object to export. (can be a model,process, flow, or matter object)
    filename : str
        The filename to export the model object to.
        without the .json extension.

    Default filename is the object name and the current date and time. Default location is the export folder.


    """

    model_dict = model_object.to_dict()

    try:
        json.dump(model_dict, open(filename, "w"))
        print(
            f'\n\n{"="*90}\n\t Exported model object to file: {filename}\n{"="*90}\n')

    except Exception as e:
        print(f"Error exporting model object to file: {e}")


def export_to_pickle(model_object, filename):
    """
    Exports the model object to a pickle file.

    Parameters
    ----------
    model_object :
        The model object to export. (can be a model,process, flow, or matter object)
    filename : str
        The filename to export the model object to.
        without the .pkl extension.

    Default filename is the object name and the current date and time. Default location is the export folder.

    """

    try:
        pickle.dump(model_object, open(filename, "wb"))
        print(
            f'\n\n{"="*90}\n\t Exported model object to file: {filename}\n{"="*90}\n')

    except Exception as e:
        print(f"Error exporting model object to file: {e}")
