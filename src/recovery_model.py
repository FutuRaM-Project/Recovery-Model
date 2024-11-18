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
from scipy.sparse import coo_array, coo_matrix, eye_array, linalg, csr_array
from typing import Tuple, List, Dict


# Definition of file/folder names within the overarching data directory
INPUT_DATA_FOLDER_NAME = "input_data"
OUTPUT_DATA_FOLDER_NAME = "output_data"

METADATA_FILENAME = "metadata.csv"
TCS_FILENAME = "TCs.csv"
INPUTS_FILENAME = "inflows.csv"
COMPOSITION_FILENAME = "composition.csv"
SOLUTION_FILENAME = "solution.csv"

class RecoveryModel:
    """Class representing the recovery model"""
    def __init__(self, data_folder: str):
        """
        Initialize the System class.
         - Defines and creates folder structure
         - Defines metadata variables such as matrix sizes, layer names and creates encoding/decoding to express resources as array indices
         - Creates matrices from composition, TC and input data
        Args:
            data_folder: directory containing input and output data for this model
        """
        # Set data folder and create structure if needed
        self.data_folder = data_folder
        if not os.path.exists(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME)):
            os.makedirs(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME))

        # Define required variables
        self.layer_names, self.encoding_dict, self.decoding_dict = self.read_metadata()
        self.dims = self.get_dims()
        self.size = np.prod(self.dims, dtype=int)

        # Read input composition, transfer coefficients and inflows and express in vector/matrix form
        self.input_matrix = self.read_inflows()
        self.composition_matrix = self.read_composition()
        self.tcs_matrix = self.read_tcs()

    def read_metadata(self) -> Tuple[List[str], dict, dict, dict]:
        """
        Reads metadata CSV file and uses it to store variables relevant for creating a functional model.

        Returns:
             - List of the layer names, including flow as the first layer
             - "Encoding" dictionary, mapping each flow/resource to a unique integer within that class
             - "Decoding" dictionary, mapping integers back to the appropriate flow/resource

        """
        metadata_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, METADATA_FILENAME))
        layer_names = list(metadata_df.columns)
        reverse_encoding = {}
        for layer in metadata_df.columns:
            items_to_encode = ([] if layer=='flow' else ['empty']) + list(metadata_df[layer].dropna())
            reverse_encoding[layer] = dict(enumerate(items_to_encode))
        encoding = {col: {v: k for k, v in dct.items()} for col, dct in reverse_encoding.items()}
        return layer_names, encoding, reverse_encoding

    def read_composition(self) -> csr_array:
        """
        Reads composition CSV file and creates a NxN matrix that can be used for the model computation.
        See the written documentation for explanation of how these matrices are created.

        :returns:
            A CSR matrix containing the composition values at appropriate indices
        """
        composition_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, COMPOSITION_FILENAME))

        # Backward compatibility with previous versions
        if 'Year' in composition_df.columns:
            composition_df = composition_df.drop(columns=['Year','parameterCode'])

        composition_df.columns = self.layer_names + ['value']

        # Add 'empty' as a value instead of NaN for all columns that are allowed to have empty values
        columns_to_fill_na = [col for col in self.layer_names if col!="flow"]
        composition_df[columns_to_fill_na] = composition_df[columns_to_fill_na].fillna('empty')

        # Encode all columns that have an encoding. 
        for column, mapping in self.encoding_dict.items():
            composition_df[column] = composition_df[column].replace(mapping)

        composition_values = composition_df["value"].values

        # The row value is the contained resource, and the column value is the containing resource. 
        # This means the row value is the specified composition and the column value is obtained by replacing the smallest material with 'empty'.
        composition_rows = composition_df[self.layer_names].values
        composition_cols = composition_df[self.layer_names].apply(HelperFunctions.set_rightmost_nonzero_to_zero, axis=1).values
        composition_rows = HelperFunctions.ravel_multi_index(multi_index=composition_rows, dimensions=self.dims)
        composition_cols = HelperFunctions.ravel_multi_index(multi_index=composition_cols, dimensions=self.dims)
        comp_matrix = HelperFunctions.create_sparse_matrix(values=composition_values, rows=composition_rows, cols=composition_cols, size=self.size)
        return comp_matrix

    def read_inflows(self) -> csr_array:
        """
        Read inflows CSV and converts it to a Nx1 matrix that can be used for the model computation. 
        See the written documentation for explanation of how these matrices are created.

        Returns:
            A CSR matrix containing the inflow values at appropriate indices
        """
        inflows_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, INPUTS_FILENAME))

        # Backward compatibility with previous version
        if len(inflows_df.columns)==5:
            inflows_df = inflows_df.drop(columns=['Year','Unit'])
            inflows_df.columns = ['flow','substance','Value']
            inflows_df.insert(1, 'layer','product')

        # Create a new dataframe that expresses the flows/resources in encodable form
        encoding_df = pd.DataFrame(columns=self.layer_names)
        for _, row in inflows_df.iterrows():
            new_row = {}
            # For each inflow, loop over the layers and fill in values one by one
            for layer in self.layer_names:
                if layer == 'flow':
                    new_row[layer] = row['flow']
                elif row['layer']==layer:
                    new_row[layer] = row['substance']
                else:
                    new_row[layer] = 'empty'
            encoding_df = encoding_df._append(new_row, ignore_index=True)

        for column, mapping in self.encoding_dict.items():
            encoding_df[column] = encoding_df[column].replace(mapping)

        inflow_values = inflows_df['Value'].values
        inflow_rows = encoding_df.values

        input_rows = HelperFunctions.ravel_multi_index(multi_index=inflow_rows, dimensions=self.dims)
        return HelperFunctions.create_vector(values=inflow_values, rows=input_rows, size=self.size)

    def read_tcs(self) -> csr_array:
        """
        Read TCs CSV and converts it to a NxN matrix that can be used for the model computation. 
        See the written documentation for explanation of how these matrices are created.

        Returns:
            A CSR matrix containing the TC values at appropriate indices
        """
        tcs_df = pd.read_csv(os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, TCS_FILENAME))

        # Backward compatibility
        tcs_df = tcs_df.drop(columns=['input_sub_layer', 'input_sub_layer_key','process','technology'])
        tcs_df.columns = ['input_flow','input_layer','input_substance','output_flow','output_layer', 'output_substance','value']

        new_tcs_df = pd.DataFrame(columns=['input_'+layer_name for layer_name in self.layer_names]+['output_'+layer_name for layer_name in self.layer_names]+['value'])
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
                    new_row['input_'+layer] = list(self.decoding_dict[layer].values())
                    new_row['output_'+layer] = list(self.decoding_dict[layer].values())
            new_tcs_df = new_tcs_df._append(new_row,ignore_index=True)
                
        for layer in self.layer_names:
            new_tcs_df = new_tcs_df.explode(['input_'+layer, 'output_'+layer])

        for column, mapping in self.encoding_dict.items():
            new_tcs_df['input_'+column] = new_tcs_df['input_'+column].replace(mapping)
            new_tcs_df['output_'+column] = new_tcs_df['output_'+column].replace(mapping)

        tcs_values = new_tcs_df["value"].values
        tcs_cols = new_tcs_df[['input_'+layer for layer in self.layer_names]].values
        tcs_rows = new_tcs_df[['output_'+layer for layer in self.layer_names]].values
        tc_rows = HelperFunctions.ravel_multi_index(multi_index=tcs_rows, dimensions=self.dims)
        tc_cols = HelperFunctions.ravel_multi_index(multi_index=tcs_cols, dimensions=self.dims)
        tc_matrix = HelperFunctions.create_sparse_matrix(values=tcs_values, cols=tc_cols, rows=tc_rows, size=self.size)
        return tc_matrix

    def solve(self) -> pd.DataFrame:
        """
        - Solve the system of linear equations
        - Return the solution back to human-readable interpretation
        - Store the solution in the output folder

        Returns:
            Dataframe containing the system's solution
        """
        # Solve the system of equations
        arr = linalg.spsolve(eye_array(self.size) - self.tcs_matrix - self.composition_matrix, self.input_matrix)

        # Decode the solution
        mask = arr != 0
        int_idx = np.nonzero(mask)[0]
        midx = HelperFunctions.unravel_multi_index(indices=int_idx,dimensions=self.dims)

        idx = pd.MultiIndex.from_arrays(midx.T, names=self.layer_names)
        solution = pd.Series(arr[mask], index=idx)
        solution = solution[solution != 0]

        solution = self.decode_label(solution.reset_index())
        solution = solution.replace('empty','')

        solution.to_csv(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME, f"solution.csv"))
        return solution

    def decode_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform a dataframe full of integer-based representation of resources back to human-readable string representation.
        
        Args:
            df: Dataframe to be decoded

        Returns:
            Decoded dataframe
        """
        decoded_df = df.copy()
        if isinstance(decoded_df.columns, pd.MultiIndex):
            for col in decoded_df.columns.levels[0]:
                decoded_df[col] = self.decode_label(decoded_df[col])
        else:
            for col in set(decoded_df.columns) & set(self.decoding_dict):
                decoded_df[col] = decoded_df[col].map(self.decoding_dict[col], na_action="ignore")
        return decoded_df

    def get_dims(self) -> tuple:
        """
        Get the dimension of each layer of the system. 
        - For flows, the dimension is the number of flows
        - For resources, the dimension is the number of resources in that layer + the 'empty' designation

        Returns:
            The shape of each layer of the system, which corresponds to the number of possible resources in that layer + an empty layer
        """
        return tuple(len(self.encoding_dict[layer]) for layer in self.layer_names)


class HelperFunctions:
    @staticmethod
    def set_rightmost_nonzero_to_zero(row: pd.Series) -> pd.Series:
        """
        Helper function to set the last of a set of values to zero
        Args:
            row: Row to be modified

        Returns:
            Modified row with the last non-zero value set to zero
        """
        nonzero_indices = row[row != 0].index
        if not nonzero_indices.empty:
            row[nonzero_indices[-1]] = 0
        return row
    
    @staticmethod
    def ravel_multi_index(multi_index: np.ndarray, dimensions: tuple) -> np.ndarray:
        """
        Helper function to convert a multi-dimensional index to a flat (1D) index

        Args:
            multi_index: Array of indices for each dimension (shape: [n, len(dimensions)])
            dimensions: The shape of the multi-dimensional array
        Returns:
            Flattened indices corresponding to the input multi-dimensional indices
        """
        dimension_products = np.array([np.prod(dimensions[i + 1 :]) if i + 1 < len(dimensions) else 1 for i in range(len(dimensions))])
        return np.dot(multi_index, dimension_products)

    @staticmethod
    def unravel_multi_index(indices: np.ndarray, dimensions: tuple) -> np.ndarray:
        """
        Helper function to convert a flat (1D) index back to the multi-dimensional representation

        Args:
            indices: Array of flat indices to be converted to multi-dimensional representation
            dimensions: The shape of the multi-dimensional array
        Returns:
            Multi-dimensional representation of the input vector
        """
        coords = np.unravel_index(indices, dimensions)
        return np.vstack(coords).T
    
    @staticmethod
    def create_sparse_matrix(values: np.ndarray, rows: np.ndarray, cols: np.ndarray, size: int) -> csr_array:
        """
        Creates a sparse matrix in CSR format based on input row, column and data values.

        Args:
            values: Values to be filled into the matrix
            rows: Row indices for each value
            cols: column indices for each value
            size: Desired size of the sparse matrix

        Returns: 
            CSR array created based on input values
        """
        coo_mat = coo_matrix((values, (rows, cols)), shape=(size, size))
        return coo_mat.tocsr()
    
    @staticmethod
    def create_vector(values: np.ndarray, rows: np.ndarray, size: int) -> csr_array:
        """
        Create an Nx1 sparse matrix based on the specified input values

        Args:
            values: Values to be filled into the vector
            rows: Row indices for each value
            size: Desired size of the vector

        Returns:
            CSR array created based on input values
        """
        cols = np.zeros_like(rows)
        coo_arr = coo_array((values, (rows, cols)), shape=(size, 1))
        return coo_arr.tocsc()
    
class InputValidation:
    def check_mass_balance():
        pass