# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello
@Date: 24.03.2024
"""
# %%
import warnings
from dataclasses import dataclass
from itertools import chain
from pprint import pformat

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from scipy.sparse import coo_array, coo_matrix, eye_array, linalg

# %%


@dataclass
class RecoveryModel:
    """Class representing the recovery model.

    Attributes:
        composition (dict): Metadata about the excel file with inflow composition.
        inputs (dict): Metadata about the excel file with mass inflows.
        tcs (dict): Metadata about the excel file with transfer coefficients.
        layer_names (tuple): Names for the multi-index levels of the system matrix (e.g. PCME).

    Methods:
        __post_init__(): Initialize the System class.
        __read_var_names(): Get variable names (products, components, materials, elements)
        __build_index(): Get the multi-index of the System.
        autocomplete(): Broadcast partial index into complete index.
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

    Notes: 1) the name of the (crossboundary) inflow(s) has to be manually added
            in the excel files and it has to be consistent across files.
    """

    metadata: dict
    composition: dict
    inputs: dict
    tcs: dict
    layer_names: tuple  # order matters
    save_intermediary_steps: bool = False
    save_duplicates: bool = False

    # ------------------------------------------------------------
    # SYSTEM INITIALIZATION
    # ------------------------------------------------------------
    def __post_init__(self):
        # def initialize(self, fill_idx="\u2205"):
        """Initialize the System class.
        Args:
            fill_idx [int or str]: The value that represents the bypassing of a hierarchical level
            (default = ∅). e.g. [F1, P1, ∅, M1] represents the mass fraction of M1 in P1 (in F1)
            which is NOT part of C1, C2, etc.
            fill_idx does NOT apply to flows (only products, components, materials and elements)
        """
        # I) Define system variables
        self.categories, self.reverse_categories, self.cat_dtype = self.read_metadata()
        self.dims = self.get_dims()
        self.size = np.prod(self.dims, dtype=int)
        self.unravel_coeffs = self.get_unravel_coeffs(self.dims)

        # II) Process composition excel file
        comp_data, comp_rows, comp_cols = self.read_composition()
        comp_rows = self.ravel_multi_index(comp_rows, self.unravel_coeffs)
        comp_cols = self.ravel_multi_index(comp_cols, self.unravel_coeffs)

        # III) Process input data (mass of flows entering the system)
        input_data, input_rows = self.read_inflows()
        input_rows = self.ravel_multi_index(input_rows, self.unravel_coeffs)

        # IV) Process transfer coefficients excel file
        tc_data, tc_rows, tc_cols = self.read_tcs()
        tc_rows = self.ravel_multi_index(tc_rows, self.unravel_coeffs)
        tc_cols = self.ravel_multi_index(tc_cols, self.unravel_coeffs)

        # V) Fill in the (square) system matrix and the Y vector
        data = np.hstack([comp_data, tc_data])
        rows = np.hstack([comp_rows, tc_rows])
        cols = np.hstack([comp_cols, tc_cols])
        self.lneqs = self.get_linear_eqs(data=data, rows=rows, cols=cols)
        self.y = self.get_y_vec(data=input_data, rows=input_rows)

    # ------------------------------------------------------------
    # I) Define system variables
    # ------------------------------------------------------------

    def read_metadata(self) -> tuple:
        """Get variable names (products, components, materials, elements) from the
        composition and TCs excel files.
        Note:   1) We assume that no 'new' products / components / materials appear
                throughout the recycling pathways (e.g. no non-mechanical treatment).
                2) From a data processing perspective, it is currently not possible to
                check which products, components, materials, elements are present in
                the TCs since the columns don't specify the layer. Therefore, we only
                get the flow names from the TCs excel file and we get the other variable
                names (P,C,M,E) from the composition excel file. This is not considered
                an issue given assumption 1).
                3) years, region and unit are not currently tracked
        """
        df = pd.read_csv(self.metadata["path"] + self.metadata["filename"])
        # create a "category" mapping that will used to speed the processing of
        # the composition, tcs and inputs data (by label encoding)
        categories = dict()
        for col in df.columns:
            categories[col] = {v: k for k, v in enumerate(df[col].dropna().unique())}
        # add 'all' symbol to the mapping (it should correspond to the highest integer)
        # but ignore flow layer (which don't have a 'all' symbol)
        for i, layer in enumerate(self.layer_names):
            if layer not in categories:
                raise ValueError(f"{layer} not found in the columns of metadata")
            if i != 0:
                dct = categories[layer]
                symbol = self.tcs["all_symbols"][layer]
                if symbol not in dct:
                    dct[symbol] = len(dct)
                else:
                    key = max(dct, key=dct.get)
                    val = dct[key].copy()
                    dct[key], dct[symbol] = dct[symbol], val
        # create pandas.CategoricalDtype based on the categories dictionary
        cat_dtype = {k: CategoricalDtype(sorted(dct, key=dct.get), ordered=True) for k, dct in categories.items()}
        # also re-route any other column labels that may be used in the csv files
        # to their corresponding category and pandas.CategoricalDtype
        for dct in (self.composition, self.inputs, self.tcs):
            for old_label, new_label in dct["mapper"].items():
                if new_label in categories:
                    categories[old_label] = categories[new_label]
                    cat_dtype[old_label] = cat_dtype[new_label]
        # create the reverse mapping for decoding
        reverse_categories = {col: {v: k for k, v in dct.items()} for col, dct in categories.items()}
        # Check for collision
        for col, dct in reverse_categories.items():
            if len(dct) != len(categories[col]):
                raise ValueError(f"Collision in mapping column {col}:\n{categories[col]}")

        return (categories, reverse_categories, cat_dtype)

    def get_dims(self) -> tuple:
        """Get the dimension of each layer of the system.
        Returns:
            tuple: The shape of each level of the system matrix.
        """
        return tuple(len(self.categories[layer]) for layer in self.layer_names)

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

    # ------------------------------------------------------------
    # II) Process composition excel file
    # ------------------------------------------------------------

    def read_composition(self) -> tuple:
        """Read composition data from Excel file and process it.
        Args:
            fill_idx (str): The value to fill missing data with.
        Returns:
            tuple: A tuple containing three arrays: data, rows and cols.
            - rows: pd.MultiIndex (with levels corresponding to F, P, C, M, E)
            - cols: pd.MultiIndex (with levels corresponding to F, P, C, M, E)
            - data: np.ndarray

        Note:   1) The excel file is assumed to have the appropriate number of
                columns (covering all hierarchichal levels). This means that
                there is no need to expand the data with 'empty' columns.
                2) the keyword "all" is NOT implemented (where [F1, P1, 'all', M1]
                would mean M1 that is contained in ALL components of P1).
        """
        df = pd.read_csv(self.composition["path"] + self.composition["filename"], dtype=self.cat_dtype)
        self.encode_label(df)
        # get the columns correspondance that will ensure consistency
        # (e.g. [Layer1, Layer2] -> [products, components])
        df.rename(mapper=self.composition["mapper"], axis=1, inplace=True)

        # ! convert csv file into (data, rows, columns) format
        # e.g. | flows | prod | comp | mat | elt | value | parameterCode |
        #      |-------|------|------|-----|-----|-------|---------------|
        #      |  F1   |  P1  |  C1  | M1  |     |  0.8  |      m-c      |
        #
        # would yield the following:
        #                           |   [F1, P1, C1, ∅, ∅] |
        #      ---------------------|----------------------|
        #       [F1, P1, C1, M1, ∅] |          0.8         |
        #      ---------------------------------------------
        # 1) the row indicates which entities we are looking at
        # 2) the column indicates which entities is being inherited from
        #    In this example, M1 represents 80% of C1 (in P1, in F1).
        # 3) "m-c" means that the line is about the share of material in
        #    components -->  rows = [F, P, C, M] & cols = [F, P, C, ∅].

        # data and rows are pretty straightforwards
        data = df["data"].values
        rows = df[list(self.layer_names)].values

        # For the columns, we first need to map the layer (in parameterCode) to
        # their corresponding integer values
        symbol = dict()
        for k, v in self.composition["parameterCode"].items():
            if v in self.categories["parameterCode"]:
                symbol[k] = self.categories["parameterCode"][v]
        # Then, for each rows in the composition dataframe we replace the outmost
        # layer by NaN (which corresponds to -1 with label encoding)
        for layer in self.composition["parameterCode"].keys():
            mask = df["parameterCode"] == symbol[layer]
            df.loc[mask, layer] = -1
        cols = df[list(self.layer_names)].values

        return (data, rows, cols)

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
        df = pd.read_csv(self.inputs["path"] + self.inputs["filename"], dtype=self.cat_dtype)
        self.encode_label(df)
        # get the columns correspondance that will ensure consistency
        # (e.g. Substance_main_parent -> products)
        df.rename(mapper=self.inputs["mapper"], axis=1, inplace=True)
        # ensure that the columns are consistent with the system layers
        # since labels have already been encoded, fill_value = -1
        df = self.broadcast_columns(df, fill_value=-1)
        # convert dataframe to (data, rows) format
        data = df["data"].values
        rows = df[list(self.layer_names)].values
        return (data, rows)

    # ------------------------------------------------------------
    # IV) Process transfer coefficients excel file
    # ------------------------------------------------------------

    def read_tcs(self) -> tuple:
        """Read input data from an Excel file and process it.
        Args:
            fill_idx (str): The value to fill missing data with.
        Returns:
            tuple: A tuple containing three arrays: rows, cols, and data.
        """
        # local variables to be used in the function
        lvls = ["input_layer1_level", "input_layer2_level", "output_layer1_level"]
        keys = ["input_layer1_key", "input_layer2_key", "output_layer1_key"]

        # ! IV.1) read excel file
        df = pd.read_csv(self.tcs["path"] + self.tcs["filename"])
        # get the columns correspondance that will ensure consistency
        # (e.g. input_flow -> inflows)
        df.rename(mapper=self.tcs["mapper"], axis=1, inplace=True)
        # Sanity check: Ensure the names of the layers are consistent
        unique = [df[col].dropna().unique() for col in lvls]
        levels = set(chain.from_iterable(unique))
        if not levels.issubset(set(self.layer_names)):
            print(f"{levels} vs {set(self.layer_names)}")
            raise ValueError("Layers in TC file are not consistent with the system layers")

        # ! IV.2) Expand columns to (F, P, C, M, E) format
        # First we expand for input top layer
        df_inflows = df[[lvls[0], keys[0]]].pivot(columns=lvls[0], values=keys[0])
        df_inflows[self.layer_names[0]] = df["inflows"]
        df_inflows = self.broadcast_columns(df_inflows, fill_value=np.nan).astype(object)
        df_inflows.columns.name = None
        # Then we update it with the info contained in the input sub layer (only for nan values)
        if df[[lvls[1], keys[1]]].notna().any().any():
            df_inflows_sub = df[[lvls[1], keys[1]]].dropna().pivot(columns=lvls[1], values=keys[1])
            df_inflows_sub[self.layer_names[0]] = df["inflows"]
            df_inflows_sub = self.broadcast_columns(df_inflows_sub, fill_value=np.nan).astype(object)
            df_inflows.update(df_inflows_sub, overwrite=False)
        # We do the same for the outflow
        df_outflows = df[[lvls[2], keys[2]]].pivot(columns=lvls[2], values=keys[2])
        df_outflows[self.layer_names[0]] = df["outflows"]
        df_outflows = self.broadcast_columns(df_outflows, fill_value=np.nan).astype(object)
        df_outflows.columns.name = None
        df_inflows.update(df_outflows, overwrite=False)
        # Note: df_inflows and df_outflows are casted as object since
        # empty columns (filled with NaN) would be casted as float otherwise
        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            pd.concat({"outflow": df_outflows, "inflow": df_inflows, "data": df["data"]}, axis=1).to_csv(
                f"{path}STEP_1_tcs_with_expanded_columns.csv"
            )

        # ! IV.3) Encode and harmonize inflows with outflows
        self.encode_label(df_inflows)
        self.encode_label(df_outflows)
        all_symbols = dict()
        for layer in self.layer_names[1:]:
            # for the inflows, the cells containing a "all" symbol are replaced by
            # the matching outflow cell if the latter is more precise
            # e.g.
            # |          inflow         ||       outflow       |
            # | F1 | P1 | 'all' |   |   || F2 |   | C1 |   |   |
            #
            # becomes
            # |          inflow         ||       outflow       |
            # | F1 | P1 |   C1  |   |   || F2 |   | C1 |   |   |
            all_symbols[layer] = self.categories[layer][self.tcs["all_symbols"][layer]]
            mask = (df_inflows[layer] == all_symbols[layer]) & (df_outflows[layer] != -1)
            df_inflows.loc[mask, layer] = df_outflows.loc[mask, layer]
            # NaN (=-1 when encoded) values implies all possible combinations
            # e.g.
            # |        inflow        |      -->     |            inflow            |
            # | F1 | P1 |   | M1 |   |              | F1 | P1 | 'all' | M1 | 'all' |
            df_inflows[layer] = df_inflows[layer].replace(-1, all_symbols[layer])
            df_outflows[layer] = df_outflows[layer].replace(-1, all_symbols[layer])

        # ! IV.4) Compute priorities in case of conflicts between rows
        # e.g
        # |          inflow         ||       outflow       |
        # | F1 | 'all' | C1 | ∅ | ∅ || F2 | ∅ | ∅ | M1 | ∅ |
        # | F1 |  P1   | C1 | ∅ | ∅ || F2 | ∅ | ∅ | M1 | ∅ |
        #
        # both rows cover the case (F1, P1, C1, M1, ∅),
        # but the second row is more precise than the first one.
        # Therefore the second row will be assigned a higher priority.
        df["priority"] = self.compute_priority(df_inflows, all_symbols=all_symbols, nan_symbol=-1)

        other_columns = df.columns.difference(lvls + keys + ["inflows", "outflows"])
        df = pd.concat({"outflow": df_outflows, "inflow": df_inflows, "info": df[other_columns]}, axis=1)

        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            self.decode_label(df).to_csv(f"{path}STEP_2_tcs_with_priorities.csv")
        # # -------------------------------

        # ! IV.5) Expand rows that contains the keyword 'all'

        #
        # In we followed the same procedure for the outflows,
        # we would end up with a cartesian product, which would create mass
        # e.g
        # |         inflow         ||         outflow        |
        # | F1 | 'all' | ∅ | ∅ | ∅ || F2 | 'all' | ∅ | ∅ | ∅ |
        #
        # would yield
        # |         inflow         ||         outflow        |
        # | F1 |  P1   | ∅ | ∅ | ∅ || F2 | 'all' | ∅ | ∅ | ∅ |
        # | F1 |  P2   | ∅ | ∅ | ∅ || F2 | 'all' | ∅ | ∅ | ∅ |
        # | F1 |  ...  | ∅ | ∅ | ∅ || F2 | 'all' | ∅ | ∅ | ∅ |
        #
        # and then:
        # |         inflow         ||         outflow        |
        # | F1 |  P1   | ∅ | ∅ | ∅ || F2 |  P1   | ∅ | ∅ | ∅ |
        # | F1 |  P1   | ∅ | ∅ | ∅ || F2 |  P2   | ∅ | ∅ | ∅ |
        # | F1 |  P2   | ∅ | ∅ | ∅ || F2 |  P1   | ∅ | ∅ | ∅ |
        # | F1 |  P2   | ∅ | ∅ | ∅ || F2 |  P2   | ∅ | ∅ | ∅ |
        # | F1 |  ...  | ∅ | ∅ | ∅ || F2 |  ...  | ∅ | ∅ | ∅ |
        #
        # So instead, 'all' symbols on the outflow side are
        # replaced by the corresponding value on the inflow side

        # reset_index so as to keep track of the original row
        df = df.reset_index(drop=False)

        # # ! ORIGINAL IDEA
        # expanded_df = df.copy().astype(object)
        # for layer in self.layer_names[1:]:  # not flows
        #     # first we replace 'all' by their corresponding tuple
        #     # e.g.
        #     # [F1, P1, 'all', M1, ∅] --> [F1, P1, (C1, C2...Cx) , M1, ∅]
        #     #
        #     # then we explode the dataframe:
        #     #                                     [F1, P1, C1, M1, ∅]
        #     # [F1, P1, (C1, C2...Cx) , M1, ∅] --> [F1, P1, C2, M1, ∅]
        #     #                                             ...
        #     #                                     [F1, P1, Cx, M1, ∅]
        #     n = all_symbols[layer]
        #     mask = df[("inflow", layer)] == n
        #     combinations = np.arange(-1, n, dtype=df[("inflow", layer)].dtype)
        #     temp_data = [combinations] * mask.sum()
        #     temp_idx = mask[mask].index
        #     new_values = pd.Series(temp_data, index=temp_idx)
        #     expanded_df.loc[mask, ("inflow", layer)] = new_values
        #     expanded_df = expanded_df.explode(("inflow", layer))
        #     mask = expanded_df[("outflow", layer)] == n
        #     expanded_df.loc[mask, ("outflow", layer)] = expanded_df.loc[mask, ("inflow", layer)]
        # df = expanded_df.astype(df.dtypes)

        # # ! OPTIMIZED ATTEMPT
        for layer in self.layer_names[1:]:
            n = all_symbols[layer]
            mask = df[("inflow", layer)] == n
            repeated_rows = np.argwhere(mask).squeeze()
            dtype = df[("inflow", layer)].dtype
            combinations = np.arange(-1, n, dtype=dtype)
            arr = np.tile(combinations, mask[mask].sum())
            temp = df.iloc[repeated_rows.repeat(n + 1)]
            temp.loc[:, ("inflow", layer)] = arr
            df = pd.concat([df.loc[~mask], temp])
            mask = df[("outflow", layer)] == n
            df.loc[mask, ("outflow", layer)] = df.loc[mask, ("inflow", layer)]

        df.columns = pd.MultiIndex.from_tuples([("info", "original row")] + df.columns.tolist()[1:])

        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            self.decode_label(df).to_csv(f"{path}STEP_3_tcs_with_expanded_rows.csv")

        # ! IV.6) Remove conflicting rows
        # ! THIS STEPS IS NOT CONSISTENT AND CAN YIELD DIFFERENT RESULTS
        # ! TO BE IMPROVED
        # now that we have expanded the dataframe, we can remove conflicting cases
        # order rows by their priority (first rows with highest priorities)
        priority = pd.IndexSlice[("info", "priority")]
        df = df.sort_values(by=priority, ascending=False)
        # in case of duplicated rows, only keep the first occurence
        # (i.e. the one with the highest priority)
        if self.save_duplicates:
            mask = df.loc[:, ["inflow", "outflow"]].duplicated(keep=False)
            df.loc[mask, :].to_csv("consolidation/duplicates.csv")
        df = df[~df.loc[:, ["inflow", "outflow"]].duplicated(keep="first")]
        # and reorganize the dataframe by the original index
        df = df.sort_index()

        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            self.decode_label(df).to_csv(f"{path}STEP_4_tcs_without_NO_conflicts.csv")

        # ! IV.7) return the dataframe in the (data, rows, cols) format
        return (df[("info", "data")].values, df["outflow"].values, df["inflow"].values)

    # ------------------------------------------------------------
    # V) Matrix filling: define the set of linear equations
    # ------------------------------------------------------------

    def get_linear_eqs(self, data, rows, cols):
        """Create the matrix of TCs (transfer coefficient) as a sparse matrix.
        Args:
            composition (tuple): A tuple containing 3 arrays: data, rows and cols.
            flow_tcs (tuple): A tuple containing 3 arrays: data, rows and cols.
        """
        coo_mat = coo_matrix((data, (rows, cols)), shape=(self.size, self.size))
        return coo_mat.tocsr()

    def get_y_vec(self, data, rows):
        """Create the vector of constant terms (Y) as a sparse matrix.
        Args:
            data (ndarray): The data values of the Y vector.
            rows (ndarray): The rows of the Y vector.
        """
        cols = np.zeros_like(rows)
        coo_arr = coo_array((data, (rows, cols)), shape=(self.size, 1))
        return coo_arr.tocsc()

    # ------------------------------------------------------------
    # VI) SYSTEM SOLVER
    # ------------------------------------------------------------

    def solve(self, output="mass", expand=False):
        """Solve the system of linear equations.
        Args:
            output (str, optional): Either in mass or mass fraction. Defaults to "mass".
        Returns:
            pd.Series: The solution of the system of linear equations as a pandas Series object.
        """
        arr = linalg.spsolve(eye_array(self.size) - self.lneqs, self.y)
        mask = arr != 0
        int_idx = np.nonzero(mask)[0]
        midx = self.unravel_index(int_idx)
        data = np.hstack([midx, arr[mask, np.newaxis]])
        solution = self.decode_label(pd.DataFrame(data, columns=list(self.layer_names) + [output]))
        if expand:
            solution = self.expand_solution(solution)
        solution = solution[solution != 0]
        solution.to_csv(f"results/solution_expand_{expand}.csv")
        return solution

    def expand_solution(self, solution, fill_idx="\u2205"):
        """Expand the solution to include all the hierarchical levels.
        Args:
            solution (pd.Series): The solution to be expanded.
            fill_idx (str, optional): The value to fill missing data with. Defaults to "\u2205".
        Returns:
            pd.Series: The expanded solution.
        """
        expanded_solution = solution.copy()

        for lvl in range(len(self.layer_names) - 1, 0, -1):
            expanded_solution = expanded_solution.unstack(level=lvl)

            exclude_sub_lvl = expanded_solution.notna().all(axis=1)
            for i in range(lvl, len(self.layer_names) - 1):
                exclude_sub_lvl &= expanded_solution.index.get_level_values(i) == fill_idx

            arr = expanded_solution.loc[exclude_sub_lvl, expanded_solution.columns != fill_idx].sum(axis=1)

            sum_lvl_not_null = expanded_solution.loc[exclude_sub_lvl, fill_idx] != 0
            sum_lvl_not_consistant = ~np.isclose(expanded_solution.loc[exclude_sub_lvl, fill_idx], arr)
            lvl_not_bypassed = expanded_solution.loc[exclude_sub_lvl].index.get_level_values(lvl - 1) != fill_idx
            mask = sum_lvl_not_null & sum_lvl_not_consistant & lvl_not_bypassed

            if mask.any():
                print(expanded_solution.loc[mask, :])
                warnings.warn("mass balance inconsistant")

            mask = ~sum_lvl_not_null & lvl_not_bypassed

            expanded_solution.loc[mask[mask].index, fill_idx] = arr
            expanded_solution = expanded_solution.stack().reorder_levels(self.layer_names)

        expanded_solution.name = solution.name
        return expanded_solution

    # ------------------------------------------------------------
    # VII) HELPERS AND GETTERS
    # ------------------------------------------------------------

    def encode_label(self, df: pd.DataFrame) -> None:
        """Label encoder for categorical data (e.g. products, components,
        materials, elements). Object and category are converted to int.

        Args:
            df (pd.DataFrame): the dataframe to encode
            categories (dict): dictionary with encoding mapping (new mapping will
            be added if not already present)

        Raises:
            ValueError: if a value in the dataframe has no mapping, eventhough the
            column is supposed to have a mapping, an error is raised.
        """
        # check if there is already an encoding mapping for the 'object' columns
        # (i.e. non-numerical), if yes, encode the columns accordingly
        mask = df.dtypes == object
        for col in set(df.columns[mask]) & set(self.cat_dtype):
            df[col] = df[col].astype(self.cat_dtype[col])
        mask = df.dtypes == object
        # for the remaining unmapped object column, update the encoding mapping
        if mask.any():
            for col in df.columns[mask]:
                df[col] = df[col].astype("category")
                self.categories[col] = {v: k for k, v in enumerate(df[col].dropna().unique())}
                self.reverse_categories[col] = {v: k for k, v in self.categories[col].items()}
        # for encoded columns, ensure that the mapping is consistent with the metadata
        mask = df.dtypes == "category"
        if mask.any():
            for col in df.columns[mask]:
                mask = df[col].cat.codes == -1
                if df.loc[mask, col].notna().any():
                    raise ValueError(f"Mismatch with metadata. Unknown value in {col}.")
                df[col] = df[col].cat.codes

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
            for col in set(decoded_df.columns) & set(self.reverse_categories):
                decoded_df[col] = decoded_df[col].map(self.reverse_categories[col], na_action="ignore")
        return decoded_df

    def broadcast_columns(self, df, fill_value=np.nan) -> pd.DataFrame:
        """Broadcast dataframe columns to layer_names format
        (e.g. [F, M, E] --> [F, ∅, ∅, M, E])

        Args:
            df (pandas.DataFrame): The partial index to be broadcasted.
            fill_idx (int or str): The value to fill the missing columns with.
        """
        if isinstance(df, pd.Series):
            df = df.to_frame()
        missing_cols = list(set(self.layer_names).difference(set(df.columns)))
        df[missing_cols] = fill_value
        additional_columns = list(set(df.columns).difference(set(self.layer_names)))
        ordered_columns = list(self.layer_names) + additional_columns
        return df.reindex(columns=ordered_columns)

    def compute_priority(self, df: pd.DataFrame, all_symbols: dict, nan_symbol: int = -1) -> np.ndarray:
        """_summary_

        Args:
            serie (pd.Series): _description_
            all_symbol (str): _description_
            nan_symbol (str): _description_

        Returns:
            _type_: _description_
        """

        def compute_column_priority(serie: pd.Series, all_symbol: int, nan_symbol: int) -> np.ndarray:
            """Compute cell priority:
            Args:
                serie (pd.Series[str]): pandas Serie
                all_symbol (str): symbol for all
                nan_symbol (str): symbol for nan values

            Returns:
                np.ndarray: array with values 0, 1 or 2:
                - 0 if original cell is "nan"
                - 1 if original cell is "all"
                - 2 otherwise
            """
            res = np.full_like(serie, 2, dtype=int)
            res[serie.eq(nan_symbol)] = 0
            res[serie.eq(all_symbol)] = 1
            return res

        priority = np.zeros(df.shape[0], dtype=int)
        for i, layer in enumerate(self.layer_names[1:]):
            col_priority = compute_column_priority(df[layer], all_symbols[layer], nan_symbol)
            priority += col_priority * 10**i
        return priority

    def ravel_multi_index(self, multi_index: np.ndarray, unravel_coeffs: np.ndarray) -> np.ndarray:
        """Get the integer-based indices corresponding to the given targets.

        Args:
            multi_index (np.ndarray): The multi-index to get the flatten integer indices for.
            unravel_coeffs (np.ndarray): The coefficients to flatten a multi-index into a 1D index.

        Returns:
            np.ndarray: The integer-based indices corresponding to the given targets.

        Notes: we add +1 to the array, since by construction the encoded array contains -1
        (= NaN) values (besides for flows). To ensure index starts at 0, we shift
        every columns by 1 (besides the first one, which correspond to the flow)
        """
        n = multi_index.shape[1] - 1
        shift = np.array([0] + [1] * n)
        return np.dot(multi_index + shift, unravel_coeffs)

    def unravel_index(self, indices: np.ndarray) -> np.ndarray:
        """Get the integer-based indices corresponding to the given targets.

        Args:
            multi_index (np.ndarray): The multi-index to get the flatten integer indices for.
            unravel_coeffs (np.ndarray): The coefficients to flatten a multi-index into a 1D index.

        Returns:
            np.ndarray: The integer-based indices corresponding to the given targets.

        Notes: we add +1 to the array, since by construction the encoded array contains -1
        (= NaN) values (besides for flows). To ensure index starts at 0, we shift
        every columns by 1 (besides the first one, which correspond to the flow)
        """
        n = len(self.dims) - 1
        shift = np.array([0] + [1] * n)
        coords = np.unravel_index(indices, self.dims)
        return np.vstack(coords).T - shift

    def __str__(self):
        """Return a string representation of the system.

        Returns:
            str: The string representation of the system.
        """
        return pformat(self.categories, indent=4)
