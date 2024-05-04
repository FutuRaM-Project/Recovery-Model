# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello
@Date: 24.03.2024
"""
# %%
from dataclasses import dataclass
from itertools import chain
from pprint import pformat

import networkx as nx
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from scipy.sparse import coo_array, coo_matrix, eye_array, linalg

# %%


@dataclass
class RecoveryModel:
    """Class representing the recovery model"""

    name: str
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

        # III) Process input data (mass of flows entering the system)
        input_data, input_rows = self.read_inflows()

        # IV) Process transfer coefficients excel file
        tc_data, tc_rows, tc_cols, self.flows_eqs, self.sub_systems = self.read_tcs()

        # convert to integer based index
        comp_rows = self.ravel_multi_index(comp_rows, self.unravel_coeffs)
        comp_cols = self.ravel_multi_index(comp_cols, self.unravel_coeffs)
        tc_rows = self.ravel_multi_index(tc_rows, self.unravel_coeffs)
        tc_cols = self.ravel_multi_index(tc_cols, self.unravel_coeffs)
        input_rows = self.ravel_multi_index(input_rows, self.unravel_coeffs)

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
                    dct[symbol] = len(dct)  # by construction, len(dct) is the highest integer
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

        # ! IV.2) Get Flow equations
        flows_eqs = df[["inflows", "outflows", "process"]].drop_duplicates()
        process = flows_eqs[["process"]].copy()  # ! to improve
        self.encode_label(process)  # ! to improve
        inflows = pd.get_dummies(flows_eqs["inflows"], dtype=int)
        inflows["process"] = flows_eqs["process"]
        outflows = pd.get_dummies(flows_eqs["outflows"], dtype=int)
        outflows["process"] = flows_eqs["process"]
        inflows, outflows = inflows.align(outflows, fill_value=0)
        inflows = inflows.groupby("process").any().astype(int)
        outflows = outflows.groupby("process").any().astype(int)
        flows_eqs = inflows - outflows

        # ! IV.3) Check how system could be divided into sub-systems
        from_ = df[["outflows", "process"]].rename(columns={"process": "from"}).drop_duplicates().set_index("outflows")
        to_ = df[["process", "inflows"]].rename(columns={"process": "to"}).drop_duplicates().set_index("inflows")
        flows_edge_list = pd.concat([from_, to_], axis=1)
        sub_systems = self.get_sub_systems(flows_edge_list)

        # ! IV.4) Expand columns to (F, P, C, M, E) format
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

        # ! IV.5) Encode and harmonize inflows with outflows
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

        # ! IV.6) Compute priorities in case of conflicts between rows
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

        # ! IV.7) Expand rows that contains the keyword 'all'

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

        # ! USING EXPLODE()   (slower)
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
        #     dtype = np.dtype(df[("inflow", layer)].dtype.name)
        #     combinations = np.arange(-1, n, dtype=dtype)
        #     temp_data = [combinations] * mask.sum()
        #     temp_idx = mask[mask].index
        #     new_values = pd.Series(temp_data, index=temp_idx)
        #     expanded_df.loc[mask, ("inflow", layer)] = new_values
        #     expanded_df = expanded_df.explode(("inflow", layer))
        #     mask = expanded_df[("outflow", layer)] == n
        #     expanded_df.loc[mask, ("outflow", layer)] = expanded_df.loc[mask][("inflow", layer)]
        # df = expanded_df.astype(df.dtypes)

        # # ! OPTIMIZED VERSION
        for layer in self.layer_names[1:]:
            n: int = all_symbols[layer]
            mask = df[("inflow", layer)] == n
            repeated_rows = np.argwhere(mask).squeeze()
            dtype = np.dtype(df[("inflow", layer)].dtype.name)
            combinations = np.arange(-1, n, dtype=dtype)
            arr = np.tile(combinations, mask[mask].sum())
            temp = df.iloc[repeated_rows.repeat(n + 1)]
            temp.loc[:, ("inflow", layer)] = arr
            df = pd.concat([df.loc[~mask], temp])
            mask = df[("outflow", layer)] == n
            df.loc[mask, ("outflow", layer)] = df.loc[mask][("inflow", layer)]

        df.columns = pd.MultiIndex.from_tuples([("info", "original row")] + df.columns.tolist()[1:])

        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            self.decode_label(df).to_csv(f"{path}STEP_3_tcs_with_expanded_rows.csv")

        # ! IV.8) Remove conflicting rows
        # ! Further test is needed to make sure that results are consistent
        # ! regardless of the expansion method used (explode() vs optimized)
        # now that we have expanded the dataframe, we can remove conflicting cases
        # order rows by their priority (first rows with highest priorities)
        priority = pd.IndexSlice[("info", "priority")]
        df = df.sort_values(by=priority, ascending=False)
        # in case of duplicated rows, only keep the first occurence
        # (i.e. the one with the highest priority)
        if self.save_duplicates:
            mask = df.loc[:, ["inflow", "outflow"]].duplicated(keep=False)
            if mask.any():
                df.loc[mask, :].to_csv(f"consolidation/{self.name}_TCs_duplicates.csv")
        df = df[~df.loc[:, ["inflow", "outflow"]].duplicated(keep="first")]
        # and reorganize the dataframe by the original index
        df = df.sort_index()

        if self.save_intermediary_steps:
            path = self.tcs["path"] + "intermediary_steps/"
            self.decode_label(df).to_csv(f"{path}STEP_4_tcs_without_NO_conflicts.csv")

        # ! IV.9) return the dataframe in the (data, rows, cols) format
        return (df[("info", "data")].values, df["outflow"].values, df["inflow"].values, flows_eqs, sub_systems)

    # ------------------------------------------------------------
    # V) Matrix filling: define the set of linear equations
    # ------------------------------------------------------------

    def get_mass_eqs(self, data, rows, cols, element_only=False):
        """Create the matrix of TCs (transfer coefficient) as a sparse matrix.

        Args:
            data (_type_): _description_
            rows (_type_): _description_
            cols (_type_): _description_
            element_only (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if element_only:  # ! TO BE IMPLEMENTED
            pass
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

        pivoted_solution = solution.unstack(level=self.layer_names[0])
        self.check_mass_balance(pivoted_solution, name)

        if aggregate:
            lst = []
            for layer, frame in self.groupby_layer(solution.reset_index(), name).items():
                frame = self.decode_label(frame).rename({layer: "key"}, axis=1)
                frame["layer"] = layer
                if pivot:

                    frame = frame.pivot(index=["layer", "key"], columns=self.layer_names[0], values=name)
                else:
                    frame = frame[[self.layer_names[0], "layer", "key", name]]
                lst.append(frame)
            solution = pd.concat(lst)

        elif pivot:
            solution = self.decode_label(
                pivoted_solution.rename(columns=self.reverse_categories[self.layer_names[0]]).reset_index()
            )
        else:
            solution = self.decode_label(solution.reset_index())

        solution.to_csv(f"results/{self.name}_solution_agg={aggregate}_pivot={pivot}.csv")
        return solution

    def groupby_layer(self, solution: pd.DataFrame, name: str) -> dict:
        """_summary_

        Args:
            solution (pd.DataFrame): _description_
            pivot (bool): _description_
            name (str): _description_

        Returns:
            _type_: _description_
        """
        groups = dict()
        for lvl, layer in enumerate(self.layer_names):
            if lvl == 0:
                continue
            cols = [self.layer_names[0]] + [layer]
            mask1 = (solution.loc[:, layer] != -1).astype(bool)
            mask2 = (solution.loc[:, list(self.layer_names[lvl + 1 :])] == -1).all(axis=1)
            # mask1 = solution.loc[:, self.layer_names[lvl]].notna().astype(bool)
            # mask2 = solution.loc[:, list(self.layer_names[lvl + 1 :])].isna().all(axis=1)
            rows = mask1 & mask2
            assert isinstance(rows, pd.Series)
            temp = solution.loc[rows, cols + [name]].groupby(cols, as_index=False).sum()
            # temp.rename({name: layer}, axis=1, inplace=True)
            groups[layer] = temp
            # res.append(temp.unstack(level=1))
        # result = pd.concat(res, axis=1)
        # result.columns.names = ["layer", "key"]
        # if pivot:
        #     return result.T
        # return result.unstack().reorder_levels([self.layer_names[0], "layer", "key"])
        return groups

    def check_mass_balance(self, solution: pd.DataFrame, name: str):
        """_summary_

        Args:
            solution (pd.DataFrame): _description_
            name (str): _description_
        """
        flows_eq = self.flows_eqs.rename(index=self.categories["process"], columns=self.categories[self.layer_names[0]])
        flows_eq, solution = flows_eq.align(solution, axis=1, fill_value=0)
        res = pd.DataFrame(
            (flows_eq.values[:, None] * solution.values[None, :]).reshape(-1, flows_eq.shape[1]),
            columns=flows_eq.columns,
        )
        new_idx = np.hstack(
            [
                np.tile(np.array(solution.index.tolist()), reps=(len(flows_eq), 1)),
                np.repeat(flows_eq.index.to_numpy(), len(solution.index))[:, None],
            ]
        )

        res.index = pd.MultiIndex.from_tuples(list(new_idx), names=list(self.layer_names[1:]) + ["process"])
        res["mass_balance"] = res.sum(axis=1)
        res = res[res["mass_balance"] != 0]
        res = res.sort_index(level=-1)
        res = self.decode_label(res.rename(columns=self.reverse_categories[self.layer_names[0]]).reset_index())
        res.to_csv(f"consolidation/{self.name}_solution_mass_balance.csv")
        mass_creation = res["mass_balance"] < 0
        assert isinstance(mass_creation, pd.Series)
        if mass_creation.any():
            print(res[mass_creation])
        return

    # ------------------------------------------------------------
    # VII) HELPERS AND GETTERS
    # ------------------------------------------------------------

    def encode_label(self, df) -> None:
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
        if isinstance(df, pd.Series):
            # ! to be implemented
            pass

        # check if there is already an encoding mapping for the 'object' columns
        # (i.e. non-numerical), if yes, encode the columns accordingly
        is_object = df.dtypes == object
        for col in set(df.columns[is_object]) & set(self.cat_dtype):
            df[col] = df[col].astype(self.cat_dtype[col])
        is_object = df.dtypes == object
        # for the remaining unmapped object column, update the encoding mapping
        assert isinstance(is_object, pd.Series)
        if is_object.any():
            for col in df.columns[is_object]:
                df[col] = df[col].astype("category")
                self.categories[col] = {v: k for k, v in enumerate(df[col].dropna().unique())}
                self.reverse_categories[col] = {v: k for k, v in self.categories[col].items()}
        del is_object
        # for encoded columns, ensure that the mapping is consistent with the metadata
        is_category = df.dtypes == "category"
        assert isinstance(is_category, pd.Series)
        if is_category.any():
            for col in df.columns[is_category]:
                is_category = df[col].cat.codes == -1
                if df.loc[is_category, col].notna().any():
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

    def get_sub_systems(self, edge_list: pd.DataFrame, source: str = "from", target: str = "to"):
        """

        Args:
            edge_list (pd.DataFrame): _description_
            source (str, optional): _description_. Defaults to "from".
            target (str, optional): _description_. Defaults to "to".
        """
        virtual_nodes = set()
        mask = edge_list["from"].isna()
        mapping = {idx: f"source_{idx}" for idx in mask[mask].index}
        virtual_nodes.update(mapping.values())
        edge_list["from"] = edge_list["from"].fillna(mapping)
        mask = edge_list["to"].isna()
        mapping = {idx: f"sink_{idx}" for idx in mask[mask].index}
        virtual_nodes.update(mapping.values())
        edge_list["to"] = edge_list["to"].fillna(mapping)
        # ! SECTION BELOW TO BE REVIEWED
        network = nx.from_pandas_edgelist(edge_list, source, target, create_using=nx.DiGraph())
        # Get the strongly connected components
        scc = list(nx.strongly_connected_components(network))
        # Create a new directed graph
        agg_network = nx.DiGraph()
        # Create a dictionary to store the components
        components_dict = {}
        # Add a node for each strongly connected component
        for i, component in enumerate(scc):
            node_name = i
            agg_network.add_node(node_name)
            components_dict[node_name] = component
        # Add edges between the components
        for i, component in enumerate(scc):
            for node in component:
                for successor in network.successors(node):
                    if successor not in component:
                        agg_network.add_edge(i, [j for j, c in enumerate(scc) if successor in c][0])
        sub_systems = []
        for i in nx.topological_sort(agg_network):
            component = components_dict[i].difference(virtual_nodes)
            if component:
                sub_systems.append(component)
        return tuple(sub_systems)

    def compute_priority(self, df: pd.DataFrame, all_symbols: dict, nan_symbol: int = -1) -> np.ndarray:
        """_summary_

        Args:
            serie (pd.Series): _description_
            all_symbol (str): _description_
            nan_symbol (str): _description_

        Returns:
            _type_: _description_
        """

        # def compute_column_priority(serie: pd.Series, all_symbol: int, nan_symbol: int) -> np.ndarray:
        #     """Compute cell priority:
        #     Args:
        #         serie (pd.Series[str]): pandas Serie
        #         all_symbol (str): symbol for all
        #         nan_symbol (str): symbol for nan values

        #     Returns:
        #         np.ndarray: array with values 0, 1 or 2:
        #         - 0 if original cell is "nan"
        #         - 1 if original cell is "all"
        #         - 2 otherwise
        #     """
        #     res = np.full_like(serie, 2, dtype=int)
        #     res[serie.eq(nan_symbol)] = 0
        #     res[serie.eq(all_symbol)] = 1
        #     return res

        priority = np.zeros(df.shape[0], dtype=int)
        for i, layer in enumerate(self.layer_names[1:]):
            col_priority = np.full_like(df[layer], 2, dtype=int)
            col_priority[df[layer].eq(nan_symbol)] = 0
            col_priority[df[layer].eq(all_symbols[layer])] = 1
            # col_priority = compute_column_priority(df[layer], all_symbols[layer], nan_symbol)
            priority += col_priority * 10**i
        return priority

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

    def ravel_multi_index(self, multi_index: np.ndarray, unravel_coeffs: np.ndarray) -> np.ndarray:
        """Flatten a multi-index into a 1D index.

        Args:
            multi_index (np.ndarray): The (encoded) multi-index to flatten
            unravel_coeffs (np.ndarray): The coefficients used to flatten a multi-index

        Returns:
            np.ndarray: The integer-based indices.
        """
        n = multi_index.shape[1] - 1
        # To ensure index starts at 0, we shift every columns by 1 (besides the 1st column,
        # which corresponds to the flow), since by construction the encoded array contains
        # -1 ()= NaN) values (besides for flows).
        shift = np.array([0] + [1] * n)
        return np.dot(multi_index + shift, unravel_coeffs)

    def unravel_index(self, indices: np.ndarray) -> np.ndarray:
        """Get the original indices from the integer-based indices.

        Args:
            indices (np.ndarray): The integer-based indices.

        Returns:
            np.ndarray: The original (encoded) indices.
        """
        n = len(self.dims) - 1
        shift = np.array([0] + [1] * n)
        coords = np.unravel_index(indices, self.dims)
        # When raveling multi-index, we shifted every columns by 1 to ensure index starts at 0,
        # since by construction the encoded array contained -1 (= NaN) values.
        # We now subtract the shift to get the original indices.
        return np.vstack(coords).T - shift

    def __str__(self):
        """Return a string representation of the system.

        Returns:
            str: The string representation of the system.
        """
        return pformat(self.categories, indent=4)
