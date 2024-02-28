# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello
@Date: 28.02.2024
"""
# %%
from dataclasses import dataclass
from pprint import pformat

import numpy as np
import pandas as pd
from scipy import sparse

if __name__ == "__main__":
    import sys

    sys.path.insert(0, "../")

from utils.helper_functions import map_array, map_multiidx_to_iloc

# %%


@dataclass
class System:
    composition_dct: dict
    inputs_dct: dict
    tc_dct: dict
    __idx_keys = ("flows", "products", "components", "materials", "elements")  # "flows" comes 1st

    # ------------------------------------------------------------
    # SYSTEM INITIALIZATION
    # ------------------------------------------------------------

    def __post_init__(self, fill_idx=-1):
        """Initialize the System class.

        Args:
            fill_idx [int or str]: The value that represents the bypassing of a hierarchical level (default = -1)
            e.g. [F1, P1, -1, M1] represents the mass fraction of M1 in P1 (in F1)
            which is NOT part of C1, C2, etc.
            fill_idx does NOT apply to flows (only products, components, materials and elements)
        """
        self.__get_var_names()
        self.__set_index(fill_idx=fill_idx)

        # ! 1) Process composition data
        comp_data, comp_rows, comp_cols = self.__read_input(dct=self.composition_dct, fill_idx=fill_idx)

        comp_data = -comp_data
        comp_rows = self.get_indexer(targets=comp_rows)
        comp_cols = self.get_indexer(targets=comp_cols)

        # ! 2) Process transfer coefficients data

        # ! 3) Process input data (mass of flows entering the system
        input_data, input_rows, _ = self.__read_input(dct=self.inputs_dct, fill_idx=fill_idx)
        input_rows = self.get_indexer(targets=input_rows)

        # ! 4) Create the matrix of TCs
        composition = (comp_data, comp_rows, comp_cols)
        flow_tcs = None
        self.__fill_tcs(composition=composition, flow_tcs=flow_tcs)

        # ! 5) Create the Y vector
        self.__fill_y(data=input_data, rows=input_rows)

    def __get_var_names(self):
        """Get variable names (products, components, materials, elements) from composition excel file."""
        self.__var = dict()

        # ! 1) Get flow names from transfer coefficients excel file
        flow_names = set()
        # get the path to the excel file with the transfer coefficients
        filepath = self.tc_dct["url"]
        # get the file sheet names
        excel = self.tc_dct["sheet"]
        # read the excel file
        file = pd.read_excel(filepath, sheet_name=None)
        # get the unique flow names from the "flows" columns of each sheet
        for sheet in file.keys():
            for flow in excel[sheet]["flows"]:
                new_flow_names = file[sheet][flow].unique()
                flow_names.update(new_flow_names)
        # sort and store the flow names
        self.__var.update({self.__idx_keys[0]: tuple(sorted(flow_names))})

        # ! 2) Get variable names (products, components, materials and elements) from composition excel file
        variable_names = {name: set() for name in self.__idx_keys[1:]}
        filepath = self.composition_dct["url"]
        mapper = self.composition_dct["mapper"]
        file = pd.read_excel(filepath, sheet_name=None)
        for sheet in file.keys():
            # Rename columns from excel file to ensure consistent naming across waste streams
            df = file[sheet].rename(mapper=mapper, axis=1)
            # Only consider columns that are either products, components, materials or elements
            for col in set(variable_names.keys()) & set(df.columns):
                new_variables = df[col].unique()
                (variable_names[col]).update(new_variables)
        self.__var.update({k: tuple(sorted(v)) for k, v in variable_names.items()})

        # 3) Get unit of input data
        self.__var["unit"] = self.inputs_dct["unit"]

    def __set_index(self, fill_idx):
        """Set the index of the System.

        Args:
            fill_idx [int or str]: The value to bypass the hierarchical decomposition.
        """
        idxs = self.__idx_keys
        iterables = [self.__var[idxs[0]]] + [[fill_idx] + list(self.__var[i]) for i in idxs[1:]]
        # store index as pd.DataFrame for easier manipulation (see __getitem__)
        __index = pd.MultiIndex.from_product(iterables, names=idxs)
        self.__index = __index.to_frame()
        # also store values of each multiindex levels for printing (see __str__)
        self.__var["index"] = {idxs[i]: {v: k for k, v in enumerate(seq)} for i, seq in enumerate(iterables)}

    def __broadcast_idxs(self, df_idx, fill_idx):
        """Broadcast partial index into complete index (e.g. [F1, M1, E1] --> [F1, -1, -1, M1, E1])

        Args:
            df_idx (pandas.DataFrame): The partial index to be broadcasted.
            fill_idx (int or str): The value to fill the missing columns with.

        Returns:
            numpy.ndarray: The complete index with the missing columns filled.

        """
        if isinstance(df_idx, pd.Series):
            df_idx = df_idx.to_frame()
        missing_cols = list(set(self.__idx_keys).difference(set(df_idx.columns)))
        new_idx = df_idx.copy()
        new_idx[missing_cols] = np.full(shape=(len(new_idx), len(missing_cols)), fill_value=fill_idx)
        return new_idx.loc[:, self.__idx_keys]  # Sort columns in the right order

    def __read_input(self, dct, fill_idx, year=None):
        """Read input data from an Excel file and process it.

        Args:
            dct (dict): A dictionary containing the file path, mapper, and sheet information.
            fill_idx (str): The value to fill missing data with.
            year (int, optional): The year to filter the data by. Defaults to None.

        Returns:
            tuple: A tuple containing three arrays: rows, cols, and data.

        """
        # Specify sheet, and columns we are interested (values need to be sequences)
        rows, cols, data = [], [], []
        filepath = dct["url"]
        mapper = dct["mapper"]
        excel = dct["sheet"]
        file = pd.read_excel(filepath, sheet_name=None)

        for sheet in file.keys():
            df = file[sheet].rename(mapper=mapper, axis=1)
            # Filter the data if necessary
            mask = df["year"] == year if year else slice(None)

            # 1) Get names of system's rows (= Systems.index) from corresponding excel columns
            row_labels = [mapper[i] for i in excel[sheet]["index"]]
            # Expand rows to nx5 shape (flows, products, components, materials, elements)
            expanded_idx = self.__broadcast_idxs(df.loc[mask, row_labels], fill_idx)
            rows.append(expanded_idx.values)  # size = n x 4

            # 2) Get names of system's columns (= Systems.columns) from corresponding excel column
            if excel[sheet]["columns"] is not None:
                col_label = [mapper[i] for i in excel[sheet]["columns"]]
                # Expand column to mx2 shape
                expanded_cols = self.__broadcast_idxs(df.loc[mask, col_label], fill_idx)
                cols.append(expanded_cols.values)  # size = m x 2

            # 3) Get data from corresponding excel column
            data_label = mapper[excel[sheet]["data"]]
            data.append(df.loc[mask, data_label].values)  # size = n x 1

        data = np.hstack(data)
        rows = np.vstack(rows)
        cols = np.vstack(cols) if cols != [] else None
        return (data, rows, cols)

    def __fill_tcs(self, composition, flow_tcs):
        """Create the matrix of TCs (transfer coefficient) as a sparse matrix.

        Args:
            composition (tuple): A tuple containing 3 arrays: data, rows and cols.
            flow_tcs (tuple): A tuple containing 3 arrays: data, rows and cols.
        """
        comp_data, comp_rows, comp_cols = composition
        # tcs_data, tcs_rows, tcs_cols = flow_tcs  # ! TO BE IMPLEMENTED

        # add ones on the diagonal
        diag_data = np.ones(len(self.index))
        diag_idxs = np.arange(len(self.index))

        # combine data, rows, cols
        data = np.hstack([comp_data, diag_data])
        rows = np.hstack([comp_rows, diag_idxs])
        cols = np.hstack([comp_cols, diag_idxs])

        coo_mat = sparse.coo_matrix((data, (rows, cols)), shape=(len(self.index), len(self.index)))
        csr_mat = coo_mat.tocsr()
        self.__tcs = csr_mat

    def __fill_y(self, data, rows):
        """Create the vector of constant terms (Y) as a sparse matrix.

        Args:
            data (ndarray): The data values of the Y vector.
            rows (ndarray): The rows of the Y vector.
        """
        cols = np.zeros_like(rows)
        coo_arr = sparse.coo_array((data, (rows, cols)), shape=(len(self.index), 1))
        csc_arr = coo_arr.tocsc()
        self.__y = csc_arr

    # ------------------------------------------------------------
    # SYSTEM SOLVER
    # ------------------------------------------------------------

    def solve(self, output="mass"):
        """Solve the system of linear equations.

        Args:
            output (str, optional): Either in mass or mass fraction. Defaults to "mass".

        Returns:
            pd.Series: The solution of the system of linear equations as a pandas Series object.
        """
        solution = sparse.linalg.spsolve(self.tcs, self.y)
        if output == "mass":
            unit = self.var["unit"]
            return pd.Series(solution, index=self.index, name=f"mass ({unit})")
        elif output == "fraction":
            unit = "%"
            # ! TO BE IMPLEMENTED

    # ------------------------------------------------------------
    # GETTERS AND SETTERS
    # ------------------------------------------------------------

    def get_indexer(self, targets):
        """Get the integer-based indices corresponding to the given targets.

        Args:
            targets (ndarray): The targets for which to retrieve the indices.

        Returns:
            ndarray: The integer-based indices corresponding to the given targets.
        """
        # format targets into appropriate index values
        midx = self.index_loc(targets)
        # Convert from 2D-ndarray[str] to 2D-ndarray[int]
        midx_as_int = map_array(arr=midx, mapper=self.__var["index"], keys=self.__idx_keys)
        # Convert from 2D-ndarray[int] to 1D-ndarray[int] using corresponding integer-based indices
        midx_iloc = map_multiidx_to_iloc(arr=midx_as_int, shape=self.index.levshape)
        return midx_iloc

    def index_loc(self, targets):
        """Format targets into appropriate index values

        Args:
            targets (Union[pd.IndexSlice, Tuple[Any, ...], np.ndarray]): The targets to retrieve values for.

        Returns:
            np.ndarray: The formated index corresponding to the targets
        """
        try:  # handle case where targets is a pd.IndexSlice
            return self.__index.loc[targets].values
        except KeyError:  # handle case where targets is a single tuple
            targets = [targets]
            return self.__index.loc[targets].values
        except ValueError:  # handle case where targets is a 2D ndarray
            return targets

    def index_iloc(self, targets):
        """Return the index values of the DataFrame at the specified integer-based positions.

        Args:
            targets (Union[int, List[int]]): The integer-based positions.

        Returns:
            pandas.Index: The index values at the specified positions.
        """
        return self.__index.iloc[targets].index

    @property
    def var(self):
        """Get the variable names of the system.

        Returns:
            dict: The variables of the system.
        """
        return self.__var

    @property
    def flows(self):
        """Get the list of flows within the system.

        Returns:
            tuple: The flows' names.
        """
        return self.__var["flows"]

    @property
    def products(self):
        """Get the list of products within the system.

        Returns:
            tuple: The products' names.
        """
        return self.__var["products"]

    @property
    def components(self):
        """Get the list of components within the system.

        Returns:
            tuple: The components' names.
        """
        return self.__var["components"]

    @property
    def materials(self):
        """Get the list of materials within the system.

        Returns:
            tuple: The materials' names.
        """
        return self.__var["materials"]

    @property
    def elements(self):
        """Get the list of elements within the system.

        Returns:
            tuple: The elements' names.
        """
        return self.__var["elements"]

    @property
    def index(self):
        """Get the index of the system.

        Returns:
            pd.MultiIndex: The index of the system.
        """
        return self.__index.index

    @property
    def tcs(self):
        """Get the transfer coefficients (TCs) matrix of the system.

        Returns:
            csr_matrix: The transfer coefficients (TCs) as a Compressed Sparse Rows matrix
        """
        return self.__tcs

    @property
    def y(self):
        """Get the constant terms that the linear equations should satisfy

        Returns:
            csc_array: constant terms Y as a Compressed Sparse Column array
        """
        return self.__y

    def __str__(self):
        """Return a string representation of the system.

        Returns:
            str: The string representation of the system.
        """
        return pformat(self.__var, indent=4)
