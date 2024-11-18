# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello / Harmjan de Vries
@Date: 24.03.2024
"""
# %%
import json
import numpy as np
import pandas as pd
import os
from pandas.api.types import CategoricalDtype
from scipy.sparse import coo_array, coo_matrix, eye_array, linalg



# Definition of file/folder names within the overarching data directory
INPUT_DATA_FOLDER_NAME = "input_data"
OUTPUT_DATA_FOLDER_NAME = "output_data"

METADATA_JSON_FILENAME = "metadata.json"
TCS_FILENAME = "TCs.csv"
INPUTS_FILENAME = "inputs.csv"
COMPOSITION_FILENAME = "composition.csv"
SOLUTION_FILENAME = "solution.csv"

class RecoveryModel:
    """Class representing the recovery model"""
    def __init__(self, data_folder: str):
        """Initialize the System class.
        Args:
            data_folder: directory containing input and output data for this model
        """
        self.data_folder = data_folder

        if not os.path.exists(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME)):
            os.makedirs(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME))


        # I) Define system variables
        self.encoding, self.reverse_encoding, self.cat_dtype, self.layer_names = self.read_metadata()

        self.dims = self.get_dims()
        self.size = np.prod(self.dims, dtype=int)
        self.unravel_coeffs = self.get_unravel_coeffs(self.dims)

        # II) Process composition excel file
        comp_data, comp_rows, comp_cols = self.read_composition()

        # III) Process input data (mass of flows entering the system)
        input_data, input_rows = self.read_inflows()

        # IV) Process transfer coefficients excel file
        tc_data, tc_rows, tc_cols = self.read_tcs()

        # convert to integer based index
        comp_rows = self.ravel_multi_index(comp_rows)
        comp_cols = self.ravel_multi_index(comp_cols)
        tc_rows = self.ravel_multi_index(tc_rows)
        tc_cols = self.ravel_multi_index(tc_cols)
        input_rows = self.ravel_multi_index(input_rows)

        # V) Fill in the (square) system matrix and the Y vector
        data = np.hstack([comp_data, tc_data])
        rows = np.hstack([comp_rows, tc_rows])
        cols = np.hstack([comp_cols, tc_cols])
        self.nnz_idx = np.unique(np.hstack([rows, cols, input_rows]))
        self.real_size = len(self.nnz_idx)

        self.data = data
        self.rows = rows
        self.cols = cols
        self.input_data = input_data
        self.input_rows = input_rows
        self.lneqs = self.get_mass_eqs(data=data, rows=rows, cols=cols)
        self.y = self.get_y_vec(data=input_data, rows=input_rows)

    # ------------------------------------------------------------
    # I) Define system variables
    # ------------------------------------------------------------
    def read_metadata(self) -> tuple:
        metadata = json.load(open(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, METADATA_JSON_FILENAME),'r'))
        layer_names = []
        reverse_encoding = {}
        cat_dtype = {}
        for layer in metadata['layers']:
            layer_name = layer['name']
            layer_names.append(layer_name)
            items_to_encode = ([] if layer_name=='flow' else ['empty']) + layer['items']
            reverse_encoding[layer_name] = dict(enumerate(items_to_encode))
            cat_dtype[layer_name] = CategoricalDtype(categories=items_to_encode, ordered=True)
        encoding = {col: {v: k for k, v in dct.items()} for col, dct in reverse_encoding.items()}
        return (encoding, reverse_encoding, cat_dtype, layer_names)

    # ------------------------------------------------------------
    # II) Process composition excel file
    # ------------------------------------------------------------

    def read_composition(self) -> tuple:
        composition_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, COMPOSITION_FILENAME), dtype=self.cat_dtype)
        if 'Year' in composition_df.columns:
            composition_df = composition_df.drop(columns=['Year','parameterCode'])
        composition_df.columns = self.layer_names + ['value']
        columns_to_fill_na = [col for col in self.layer_names if col!="flow"]
        composition_df[columns_to_fill_na] = composition_df[columns_to_fill_na].fillna('empty')
        # Encode all columns htat have an encoding. 
        for column, mapping in self.encoding.items():
            composition_df[column] = composition_df[column].replace(mapping)

        composition_values = composition_df["value"].values
        composition_rows = composition_df[self.layer_names].values
        composition_cols = composition_df[self.layer_names].apply(HelperFunctions.set_rightmost_nonzero_to_zero, axis=1).values
        return composition_values, composition_rows, composition_cols

    # ------------------------------------------------------------
    # III) Process input data (mass of flows entering the system)
    # ------------------------------------------------------------

    def read_inflows(self) -> tuple:
        """Read input data from an Excel file and process it.
        Args:
            dct (dict): A dictionary containing the file path, mapper, and sheet information.
            fill_idx (str): The value to fill missing data with.
            year (int, optional): The year to filter the data by. Defaults to None.
        Returns:
            tuple: A tuple containing three arrays: rows and data.
        """
        df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, INPUTS_FILENAME), dtype=self.cat_dtype)
        # can be removed if input format changed
        if len(df.columns)==5:
            df = df.drop(columns=['Year','Unit'])
            df.columns = ['flow','substance','Value']
            df.insert(1, 'layer','product')

        encodable_df = pd.DataFrame(columns=self.layer_names)
        for _, row in df.iterrows():
            new_row = {}
            for layer in self.layer_names:
                if layer == 'flow':
                    new_row[layer] = row['flow']
                elif row['layer']==layer:
                    new_row[layer] = row['substance']
                else:
                    new_row[layer] = 'empty'
            encodable_df = encodable_df._append(new_row, ignore_index=True)

        for column, mapping in self.encoding.items():
            encodable_df[column] = encodable_df[column].replace(mapping)

        values = df['Value'].values
        rows = encodable_df.values
        return (values, rows)


    def read_tcs(self) -> tuple:
        """
        """
        tcs_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, TCS_FILENAME))
        tcs_df = tcs_df.drop(columns=['input_sub_layer', 'input_sub_layer_key','process','technology'])
        tcs_df.columns = ['input_flow','input_layer','input_substance','output_flow','output_layer', 'output_substance','value']

        new_tcs_df = pd.DataFrame(columns=['input_'+layer_name for layer_name in self.layer_names]+['output_'+layer_name for layer_name in self.layer_names]+['value'])
        # Here I need to sort them so that FILLED elements, materials are always last.
        for _, row in tcs_df.iterrows():
            new_row = {}
            new_row['input_flow'] = row['input_flow']
            new_row['output_flow'] = row['output_flow']
            new_row['value'] = row['value']
            for layer in self.layer_names:
                if layer == 'flow':
                    continue
                if row['input_layer']==layer:
                    new_row['input_'+layer] = row['input_substance']
                    new_row['output_'+layer] = row['input_substance']
                elif row['output_layer']==layer:
                    new_row['input_'+layer] = row['output_substance']
                    new_row['output_'+layer] = row['output_substance']
                else:
                    new_row['input_'+layer] = list(self.reverse_encoding[layer].values())
                    new_row['output_'+layer] = list(self.reverse_encoding[layer].values())
            new_tcs_df = new_tcs_df._append(new_row,ignore_index=True)
                
        for layer in self.layer_names:
            new_tcs_df = new_tcs_df.explode(['input_'+layer, 'output_'+layer])

        for column, mapping in self.encoding.items():
            new_tcs_df['input_'+column] = new_tcs_df['input_'+column].replace(mapping)
            new_tcs_df['output_'+column] = new_tcs_df['output_'+column].replace(mapping)

        tcs_values = new_tcs_df["value"].values
        tcs_cols = new_tcs_df[['input_'+layer for layer in self.layer_names]].values
        tcs_rows = new_tcs_df[['output_'+layer for layer in self.layer_names]].values

        return tcs_values, tcs_rows, tcs_cols

    # ------------------------------------------------------------
    # V) Matrix filling: define the set of linear equations
    # ------------------------------------------------------------

    def get_mass_eqs(self, data, rows, cols):
        """Create the matrix of TCs (transfer coefficient) as a sparse matrix.

        Args:
            data (_type_): _description_
            rows (_type_): _description_
            cols (_type_): _description_
            element_only (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        coo_mat = coo_matrix((data, (rows, cols)), shape=(self.size, self.size))
        return coo_mat.tocsr()

    def get_y_vec(self, data, rows, element_only=False):
        """Create the vector of constant terms (Y) as a sparse matrix.

        Args:
            data (_type_): _description_
            rows (_type_): _description_
            element_only (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if element_only:  # ! TO BE IMPLEMENTED
            pass
        cols = np.zeros_like(rows)
        coo_arr = coo_array((data, (rows, cols)), shape=(self.size, 1))
        return coo_arr.tocsc()

    # ------------------------------------------------------------
    # VI) SYSTEM SOLVER
    # ------------------------------------------------------------

    def solve(self, aggregate: bool = True, pivot: bool = True, name: str = "data"):
        """Solve the system of linear equations.

        Args:
            aggregate (bool, optional): _description_. Defaults to True.
            pivot (bool, optional): _description_. Defaults to True.
            name (str, optional): _description_. Defaults to "data".
            fill_idx (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        arr = linalg.spsolve(eye_array(self.size) - self.lneqs, self.y)
        mask = arr != 0
        int_idx = np.nonzero(mask)[0]
        midx = self.unravel_index(int_idx)
        # data = np.hstack([midx, arr[mask, np.newaxis]])
        # solution = self.decode_label(pd.DataFrame(data, columns=list(self.layer_names) + [name]))
        idx = pd.MultiIndex.from_arrays(midx.T, names=self.layer_names)
        solution = pd.Series(arr[mask], index=idx, name=name)
        solution = solution[solution != 0]

        solution = self.decode_label(solution.reset_index())
        solution = solution.replace('empty','')

        solution.to_csv(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME, f"solution_agg={aggregate}_pivot={pivot}.csv"))
        return solution

    def decode_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """Decode the label encoded dataframe.
        Args:
            df (pd.DataFrame): the dataframe to decode

        Returns:
            pd.DataFrame: the decoded dataframe
        """
        decoded_df = df.copy()
        if isinstance(decoded_df.columns, pd.MultiIndex):
            for col in decoded_df.columns.levels[0]:
                decoded_df[col] = self.decode_label(decoded_df[col])
        else:
            for col in set(decoded_df.columns) & set(self.reverse_encoding):
                decoded_df[col] = decoded_df[col].map(self.reverse_encoding[col], na_action="ignore")
        return decoded_df

    def get_dims(self) -> tuple:
        """Get the dimension of each layer of the system.
        Returns:
            tuple: The shape of each level of the system matrix.
        """
        return tuple(len(self.encoding[layer]) for layer in self.layer_names)

    def get_unravel_coeffs(self, shape) -> np.ndarray:
        """Get the coefficients to flatten a multi-index into a 1D index.

        Args:
            shape (tuple): The dimensional space

        Returns:
            ndarray: The integer-based indices = (a0, a1, ..., an-1, an), with:
                a0 = shape[1] * shape[2] * ... * shape[n] * 1,
                a1 = shape[2] * ... * shape[n] * 1,
                an-1 = shape[n]
                an = 1
        """
        return np.array([np.prod(shape[i + 1 :]) if i + 1 < len(shape) else 1 for i in range(len(shape))])

    def ravel_multi_index(self, multi_index: np.ndarray) -> np.ndarray:
        return np.dot(multi_index, self.unravel_coeffs)

    def unravel_index(self, indices: np.ndarray) -> np.ndarray:
        """Get the original indices from the integer-based indices.

        Args:
            indices (np.ndarray): The integer-based indices.

        Returns:
            np.ndarray: The original (encoded) indices.
        """
        coords = np.unravel_index(indices, self.dims)
        return np.vstack(coords).T
# %%

class HelperFunctions:
    def set_rightmost_nonzero_to_zero(row: pd.Series) -> pd.Series:
        """Sets the rightmost non-zero value in a row to zero."""
        nonzero_indices = row[row != 0].index
        if not nonzero_indices.empty:
            row[nonzero_indices[-1]] = 0
        return row
    
class InputValidation:
    def check_mass_balance():
        pass