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
from scipy.sparse import coo_array, coo_matrix, linalg
from utils.helper_functions import map_array, map_multiidx_to_iloc

# if __name__ == "__main__":  # when trying to run the script from the terminal
#     import sys

#     sys.path.insert(0, "../")


# %%


@dataclass
class System:
    """Class representing the recovery model.

    Attributes:
        composition_dct (dict): Metadata about the excel file with inflow composition.
        inputs_dct (dict): Metadata about the excel file with mass inflows.
        tc_dct (dict): Metadata about the excel file with transfer coefficients.
        __idx_keys (tuple): Names for the multi-index levels of the system matrix (e.g. PCME).

    Methods:
        __post_init__(): Initialize the System class.
        __get_var_names(): Get variable names (products, components, materials, elements)
        __get_index(): Get the multi-index of the System.
        __broadcast_idxs(): Broadcast partial index into complete index.
        __read_input(): Read input data from an Excel file and process it.
        __get_linear_eqs(): Create the system matrix of linear equations as a sparse matrix.
        __get_y_vec(): Create the vector of constant terms (Y) as a sparse matrix.
        solve(): Solve the system of linear equations.

    Getters and Setters:
        get_indexer(): Get the integer-based indices corresponding to the given targets.
        index_loc(): Format targets into appropriate index values.
        index_iloc(): Return the index values of the DataFrame at the specified integer-based positions.
        var(): Get the variable names of the system.
        flows(): Get the list of flows within the system.
        products(): Get the list of products within the system.
        components(): Get the list of components within the system.
        materials(): Get the list of materials within the system.
        elements(): Get the list of elements within the system.
        index(): Get the index of the system.
        tcs(): Get the transfer coefficients (TCs) matrix of the system.
        y(): Get the constant terms that the linear equations should satisfy
        __str__(): Return a string representation of the system.
    """

    composition_dct: dict
    inputs_dct: dict
    tc_dct: dict
    __idx_keys = ("flows", "products", "components", "materials", "elements")  # "flows" comes 1st

    # ------------------------------------------------------------
    # I. SYSTEM INITIALIZATION
    # ------------------------------------------------------------

    def __post_init__(self, fill_idx=-1):
        """Initialize the System class.

        Args:
            fill_idx [int or str]: The value that represents the bypassing of a hierarchical level (default = -1)
            e.g. [F1, P1, -1, M1] represents the mass fraction of M1 in P1 (in F1)
            which is NOT part of C1, C2, etc.
            fill_idx does NOT apply to flows (only products, components, materials and elements)
        """
        # ! I.1) Define system variables
        # Get names from excel files (for flows, products, components, materials, elements)
        self.__var = self.__get_var_names()
        # Build the multi-index of the system matrix
        self.__index = self.__get_index(fill_idx=fill_idx)

        # ! I.2) Process composition data
        comp_data, comp_rows, comp_cols = self.__read_input(dct=self.composition_dct, fill_idx=fill_idx)
        comp_rows = self.get_indexer(targets=comp_rows)
        comp_cols = self.get_indexer(targets=comp_cols)

        # ! I.3) Process transfer coefficients data
        # TO BE IMPLEMENTED

        # ! I.4) Process input data (mass of flows entering the system)
        input_data, input_rows, _ = self.__read_input(dct=self.inputs_dct, fill_idx=fill_idx)
        input_rows = self.get_indexer(targets=input_rows)

        # ! I.5) Fill in the (square) system matrix and the Y vector
        comp_data *= -1  # ! EXPLAIN CLEARLY WHY WE MULTIPLY BY -1
        composition = (comp_data, comp_rows, comp_cols)
        flow_tcs = None
        self.__ln_eqs = self.__get_linear_eqs(composition=composition, flow_tcs=flow_tcs)
        self.__y = self.__get_y_vec(data=input_data, rows=input_rows)

    # ------------------------------------------------------------
    # I.1) Define system variables
    # ------------------------------------------------------------

    def __get_var_names(self):
        """Get variable names (products, components, materials, elements) from composition excel file.

        Note:   We assume that no 'new' products / components / materials appear throughout
                the recycling pathways (e.g. no non-mechanical treatment processes).
        """
        __var = dict()

        # ! I.1.1) Get flow names from transfer coefficients excel file
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
        __var.update({self.__idx_keys[0]: tuple(sorted(flow_names))})

        # ! I.1.2) Get variable names (products, components, materials and elements) from composition excel file
        variable_names = {name: set() for name in self.__idx_keys[1:]}
        # get the path to the excel file with the composition data
        filepath = self.composition_dct["url"]
        # get the columns correspondance that will ensure consistency
        # (e.g. ["value", "tc", "share"] -> "data")
        mapper = self.composition_dct["mapper"]
        # read the excel file
        file = pd.read_excel(filepath, sheet_name=None)
        for sheet in file.keys():
            # Rename columns from excel file to ensure consistent naming across waste streams
            df = file[sheet].rename(mapper=mapper, axis=1)
            # Only consider columns that are either products, components, materials or elements
            # How other columns (e.g. "years", "region") would be tracked remains to be determined.
            for col in set(variable_names.keys()) & set(df.columns):
                new_variables = df[col].unique()
                (variable_names[col]).update(new_variables)
        # store P, C, M and E names
        __var.update({k: tuple(sorted(v)) for k, v in variable_names.items()})

        # ! I.1.3) Get unit of input data
        __var["unit"] = self.inputs_dct["unit"]

        # return all variable names
        return __var

    def __get_index(self, fill_idx):
        """Set the index of the System.

        Args:
            fill_idx [int or str]: The value to bypass the hierarchical decomposition.
        """
        idxs = self.__idx_keys
        # build the following nested list
        #  [[F1, F2, ..., Fxx],
        #   [-1, P1, P2, ..., Pxx],
        #   [-1, C1, C2, ..., Cxx],
        #   [-1, M1, M2, ..., Mxx],
        #   [-1, E1, E2, ..., Exx]]
        iterables = [self.__var[idxs[0]]] + [[fill_idx] + list(self.__var[i]) for i in idxs[1:]]
        # store values of each multi-index levels for printing (see __str__)
        self.__var["index"] = {idxs[i]: {v: k for k, v in enumerate(seq)} for i, seq in enumerate(iterables)}
        # return the multi-index as pd.DataFrame for easier manipulation (see __getitem__)
        __index = pd.MultiIndex.from_product(iterables, names=idxs)
        return __index.to_frame()

    # ------------------------------------------------------------
    # I.2-I.4) Helper function to process data
    # ------------------------------------------------------------

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
        # get the path to the excel file with the data to be processed
        filepath = dct["url"]
        # get the columns correspondance that will ensure consistency
        mapper = dct["mapper"]
        # get the sheet and read the excel file
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
        cols = np.vstack(cols) if cols != [] else None  # can't remember why it is different for cols
        return (data, rows, cols)

    # ------------------------------------------------------------
    # I.5.1) Matrix filling: define the set of linear equations
    # ------------------------------------------------------------

    def __get_linear_eqs(self, composition, flow_tcs):
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

        coo_mat = coo_matrix((data, (rows, cols)), shape=(len(self.index), len(self.index)))
        csr_mat = coo_mat.tocsr()
        return csr_mat

    # ------------------------------------------------------------
    # I.5.2) Matrix filling: Y vector
    # ------------------------------------------------------------

    def __get_y_vec(self, data, rows):
        """Create the vector of constant terms (Y) as a sparse matrix.

        Args:
            data (ndarray): The data values of the Y vector.
            rows (ndarray): The rows of the Y vector.
        """
        cols = np.zeros_like(rows)
        coo_arr = coo_array((data, (rows, cols)), shape=(len(self.index), 1))
        csc_arr = coo_arr.tocsc()
        return csc_arr

    # ------------------------------------------------------------
    # II) SYSTEM SOLVER
    # ------------------------------------------------------------

    def solve(self, output="mass"):
        """Solve the system of linear equations.

        Args:
            output (str, optional): Either in mass or mass fraction. Defaults to "mass".

        Returns:
            pd.Series: The solution of the system of linear equations as a pandas Series object.
        """
        solution = linalg.spsolve(self.__ln_eqs, self.__y)
        if output == "mass":
            unit = self.var["unit"]
            return pd.Series(solution, index=self.index, name=f"mass ({unit})")
        elif output == "fraction":
            unit = "%"
            # ! TO BE IMPLEMENTED

    # ------------------------------------------------------------
    # III) HELPERS, GETTERS AND SETTERS
    # ------------------------------------------------------------

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
        return new_idx.loc[:, list(self.__idx_keys)]  # Sort columns in the right order

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
        shape = self.index.levshape
        midx_iloc = map_multiidx_to_iloc(arr=midx_as_int, shape=shape)
        return midx_iloc

    def index_loc(self, candidates):
        """Format candidates index into correct system index

        Args:
            candidates: candidate index to be format Possible types are:
                - string (in this case it is assumed that it corresponds to the flow level)
                - tuple[str] / list[str] / np.ndarray[str]
                - nested list / nested tuple / 2d ndarray of strings
                - pd.IndexSlice

        Returns:
            2d np.ndarray: The formated index corresponding to the candidates
        """
        if isinstance(candidates, str):
            candidates = (candidates,)
        try:  # this should handle most cases
            idxs = self.__index.loc[tuple(candidates), :].values
        except KeyError:  # but in case candidates is a nested list/tuple
            candidates = [tuple(row) for row in candidates]
            idxs = self.__index.loc[candidates, :].values

        if len(idxs.shape) == 1:
            return idxs[np.newaxis, :]  # make sure it is 2D
        return idxs

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
    def index(self) -> pd.MultiIndex:
        """Get the index of the system.

        Returns:
            pd.MultiIndex: The index of the system.
        """
        return self.__index.index

    @property
    def idx(self):
        """Get the index of the system.

        Returns:
            pd.MultiIndex: The index of the system.
        """
        return self.__index  # ! temp

    @property
    def lneqs(self):
        """Get the transfer coefficients (TCs) matrix of the system.

        Returns:
            csr_matrix: The transfer coefficients (TCs) as a Compressed Sparse Rows matrix
        """
        return self.__ln_eqs

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
