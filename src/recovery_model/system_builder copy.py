# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello
@Date: 28.02.2024
"""
# %%
import warnings
from dataclasses import dataclass
from itertools import chain, product
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

    composition_dct: dict
    inputs_dct: dict
    tc_dct: dict
    layer_names = ("flows", "products", "components", "materials", "elements")  # order matters
    save_intermediary_steps = True

    # ------------------------------------------------------------
    # I. SYSTEM INITIALIZATION
    # ------------------------------------------------------------

    def __post_init__(self, fill_idx="\u2205"):
        """Initialize the System class.
        Args:
            fill_idx [int or str]: The value that represents the bypassing of a hierarchical level
            (default = ∅). e.g. [F1, P1, ∅, M1] represents the mass fraction of M1 in P1 (in F1)
            which is NOT part of C1, C2, etc.
            fill_idx does NOT apply to flows (only products, components, materials and elements)
        Notes:
            "\u2205" = ∅
        """
        # ! I.1) Define system variables
        # Get names from excel files (for flows, products, components, materials, elements)
        self.__var = self.__read_var_names()
        # Build the multi-index of the system matrix
        self.__index = self.__build_index(fill_idx=fill_idx)

        # ! I.2) Process composition excel file
        comp_data, comp_rows, comp_cols = self.__read_composition(fill_idx=fill_idx)
        # comp_rows = self.get_indexer(comp_rows)
        # comp_cols = self.get_indexer(comp_cols)

        # ! I.3) Process transfer coefficients excel file
        tc_data, tc_rows, tc_cols = self.__read_tcs(fill_idx=fill_idx)
        # tc_rows = self.get_indexer(tc_rows)
        # tc_cols = self.get_indexer(tc_cols)

        # ! I.4) Process input data (mass of flows entering the system)
        input_data, input_rows = self.__read_inflows(fill_idx=fill_idx)
        # input_rows = self.get_indexer(input_rows)

        # test
        self.input_rows = input_rows
        self.input_data = input_data
        self.comp_rows = comp_rows
        self.comp_cols = comp_cols
        self.comp_data = comp_data
        self.tc_rows = tc_rows
        self.tc_cols = tc_cols
        self.tc_data = tc_data

        # # ! I.5) Fill in the (square) system matrix and the Y vector
        # comp_data *= -1  # ! EXPLAIN CLEARLY WHY WE MULTIPLY BY -1
        # composition = (comp_data, comp_rows, comp_cols)
        # flow_tcs = None
        # self.__ln_eqs = self.__get_linear_eqs(composition=composition, flow_tcs=flow_tcs)
        # self.__y = self.__get_y_vec(data=input_data, rows=input_rows)

    # ------------------------------------------------------------
    # I.1) Define system variables
    # ------------------------------------------------------------

    def __read_var_names(self) -> dict:
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
        __var = dict()

        # ! I.1.1) Get flow names from transfer coefficients excel file
        flow_names = set()
        # read the TCs excel file
        filepath = self.tc_dct["url"]
        sheet = self.tc_dct["sheet"]
        df = pd.read_excel(filepath, sheet_name=sheet)
        # get the columns correspondance that will ensure consistency
        # (e.g. ["Layer1", "Layer2"] -> ["products", "components"])
        mapper = self.tc_dct["mapper"]
        df = df.rename(mapper=mapper, axis=1)
        # get the unique flow names from the "flows" columns
        for flow in ["inflows", "outflows"]:
            new_flow_names = df[flow].unique()
            flow_names.update(new_flow_names)
        # sort and store the flow names
        __var.update({self.layer_names[0]: tuple(sorted(flow_names))})

        # ! I.1.2) Get other variable names (P,C,M,E) from composition excel file
        variable_names = {name: set() for name in self.layer_names[1:]}
        # get the path to the excel file with the composition data
        filepath = self.composition_dct["url"]
        sheet = self.composition_dct["sheet"]
        df = pd.read_excel(filepath, sheet_name=sheet)
        # get the columns correspondance that will ensure consistency
        # (e.g. ["Layer1", "Layer2"] -> ["products", "components"])
        mapper = self.composition_dct["mapper"]
        df = df.rename(mapper=mapper, axis=1)
        # Only consider columns that are either products, components, materials or elements
        for col in set(variable_names.keys()) & set(df.columns):
            new_variables = df[col].dropna().unique()
            (variable_names[col]).update(new_variables)
        # store P, C, M and E names
        __var.update({k: tuple(sorted(v)) for k, v in variable_names.items()})

        # ! I.1.3) Get unit of input data
        # to be implemented

        return __var

    def __build_index(self, fill_idx) -> pd.DataFrame:
        """Set the index of the System.
        Args:
            fill_idx [int or str]: The value to bypass the hierarchical decomposition.

        Note:   1) flows can NOT be null
                2) It is possible to bypass a hierarchical level (i.e. P, C or M), but
                two distincts level must be filled with their in between levels. Hence,
                the following cases are impossible:
                    - For 5 hierarchical levels (F,P,C,M,E):
                        [F, P, C, ∅, E]    case 1
                        [F, ∅, C, ∅, E]    case 2
                        [F, P, ∅, M, E]    case 3
                        [F, P, ∅, M, ∅]    case 4
                        [F, P, ∅, ∅, E]    case 5
                    - For 4 hierarchical levels (e.g. F,P,M,E):
                        [F, P, ∅, E]    case 1
                    - For 3 hierarchical levels or less (e.g. F,M,E):
                        all cases are possible
        """
        levels = self.layer_names
        # build the following nested list
        #  [[F1, F2, ..., Fxx],        <-- flows
        #   [∅, P1, P2, ..., Pxx],     <-- products
        #   [∅, C1, C2, ..., Cxx],     <-- components
        #   [∅, M1, M2, ..., Mxx],     <-- materials
        #   [∅, E1, E2, ..., Exx]]        <-- elements
        iterables = [self.__var[levels[0]]] + [(fill_idx,) + self.__var[i] for i in levels[1:]]
        midx = pd.DataFrame(data=list(product(*iterables)), columns=levels)
        # if len(self.__var) == 5:
        #     lvl1_notna = midx[levels[1]] != fill_idx  # products
        #     lvl2_notna = midx[levels[2]] != fill_idx  # components
        #     lvl3_notna = midx[levels[3]] != fill_idx  # materials
        #     lvl4_notna = midx[levels[4]] != fill_idx  # elements
        #     lvl2_isna = ~lvl2_notna
        #     lvl3_isna = ~lvl3_notna
        #     case_1_2 = lvl2_notna & lvl3_isna & lvl4_notna
        #     case_3_4_5 = lvl1_notna & lvl2_isna & (lvl3_notna | lvl4_notna)
        #     rows_to_remove = midx.loc[case_1_2 | case_3_4_5].index
        #     midx = midx.drop(index=rows_to_remove).reset_index(drop=True)
        # elif len(self.__var) == 4:
        #     lvl1_notna = midx[levels[1]] != fill_idx
        #     lvl2_isna = midx[levels[2]] == fill_idx
        #     lvl3_notna = midx[levels[3]] != fill_idx
        #     case_1 = lvl1_notna & lvl2_isna & lvl3_notna
        #     rows_to_remove = midx.loc[case_1].index
        #     midx = midx.drop(index=rows_to_remove).reset_index(drop=True)

        # store values of each multi-index levels for printing (see __str__)
        self.__var["index"] = {levels[i]: {v: k for k, v in enumerate(seq)} for i, seq in enumerate(iterables)}
        # # return the multi-index as pd.DataFrame for easier manipulation (see __getitem__)
        # return pd.MultiIndex.from_product(iterables, names=levels).to_frame()

        midx.index = pd.MultiIndex.from_frame(midx)
        return midx

    # ------------------------------------------------------------
    # I.2) Process composition excel file
    # ------------------------------------------------------------

    def __read_composition(self, fill_idx):
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
        # ! I.2.1) read excel file
        filepath = self.composition_dct["url"]
        sheet = self.composition_dct["sheet"]
        df = pd.read_excel(filepath, sheet_name=sheet)
        # get the columns correspondance that will ensure consistency
        # (e.g. ["Layer1", "Layer2"] -> ["products", "components"])
        mapper = self.composition_dct["mapper"]
        df = df.rename(mapper=mapper, axis=1).fillna(fill_idx)

        # ! I.2.2) Filter data by year / region
        # ! To be implemented
        # year = None
        # region = None
        # mask_year = df["year"] == year if year else slice(None)
        # mask_region = df["region"] == region if region else slice(None)
        # mask = mask_year & mask_region

        # ! I.2.3) convert excel file into (data, rows, columns) format
        # ! to build the sparse system matrix
        # e.g. | flows | prod | comp | mat | elt | value | layer_code |
        #      |-------|------|------|-----|-----|-------|------------|
        #      |  F1   |  P1  |  C1  | M1  |     |  0.8  |    m-c     |
        #
        # would yield the following:
        #                           |   [F1, P1, C1, ∅, ∅] |
        #      ---------------------|----------------------|
        #       [F1, P1, C1, M1, ∅] |          0.8         |
        #      ------------------------------------------------
        # 1) the row indicates which entities we are looking at
        # 2) the column indicates which entities is being inherited from
        #    In this example, M1 represents 80% of C1 (in P1, in F1).
        # 3) "m-c" means that the line is about the share of material in
        #    components -->  rows = [F, P, C, M] & cols = [F, P, C, ∅].
        #
        # data and rows are pretty straightforward!
        data = df["data"].values
        rows = df.set_index(list(self.layer_names)).index
        # but columns requires a bit more processing
        # the idea is to replace the last layer that contains information
        # by 'fill_dx' (= ∅).  In the example above, M1 becomes ∅.
        temp = df.copy()
        for layer, layer_codes in self.composition_dct["data_processing"].items():
            mask = temp["layer_code"].isin(set(layer_codes))
            temp.loc[mask, layer] = fill_idx
        cols = temp.set_index(list(self.layer_names)).index

        return (data, rows, cols)

    # ------------------------------------------------------------
    # I.3) Process transfer coefficients excel file
    # ------------------------------------------------------------

    def __read_tcs(self, fill_idx):
        """Read input data from an Excel file and process it.
        Args:
            fill_idx (str): The value to fill missing data with.
        Returns:
            tuple: A tuple containing three arrays: rows, cols, and data.
        """
        # local variables to be used in the function
        layer_lvls = ["input_layer1_level", "input_layer2_level", "output_layer1_level"]
        layer_keys = ["input_layer1_key", "input_layer2_key", "output_layer1_key"]

        # ! I.3.1) read excel file
        filepath = self.tc_dct["url"]
        sheet = self.tc_dct["sheet"]
        df = pd.read_excel(filepath, sheet_name=sheet)
        # get the columns correspondance that will ensure consistency
        # (e.g. ["Layer1", "Layer2"] -> ["products", "components"])
        mapper = self.tc_dct["mapper"]
        df = df.rename(mapper=mapper, axis=1)

        # Sanity check: Ensure the names of the layers are consistent
        unique = [df[col].unique() for col in layer_lvls]
        levels = set(chain.from_iterable(unique)) - {np.nan}
        if not levels.issubset(set(self.layer_names)):
            raise ValueError("Layers in TC file are not consistent with the system layers")

        # ! I.3.2) Expand columns to (F, P, C, M, E) format
        df_inflows = self.__expand_columns(df, layer_lvls[0], layer_keys[0], "inflows")
        df_inflows2 = self.__expand_columns(df, layer_lvls[1], layer_keys[1])
        df_outflows = self.__expand_columns(df, layer_lvls[2], layer_keys[2], "outflows")
        df_inflows.update(df_inflows2, overwrite=False)
        df_inflows.update(df_outflows, overwrite=False)
        df_inflows = self.__replace_all_symbols(df_inflows, self.tc_dct["all_symbol"])
        df_outflows = self.__replace_all_symbols(df_outflows, self.tc_dct["all_symbol"])
        df = self.__combine_dataframes(df_inflows, df_outflows, df)

        # ! I.3.3) Compute priorities in case of conflicts between rows
        df[("other", "priority")] = self.compute_row_priority(
            df=df["inflow"].loc[:, self.layer_names[1:]],
            nan_symbol=fill_idx,
        )

        # ! OPTIONAL
        if self.save_intermediary_steps:
            df.to_csv("STEP_1_tc_with_expanded_columns&priorities.csv")

        # ! I.3.4) Expand rows that contains the keyword 'all'
        df = self.__expand_rows(df, self.layer_names[1:], fill_idx)

        # ! OPTIONAL
        if self.save_intermediary_steps:
            df.to_csv("STEP_2_tc_with_expanded_columns&rows_with_conflict.csv")

        # ! I.3.5) Remove conflicting rows
        df = self.__remove_conflicting_rows(df)

        # ! OPTIONAL
        if self.save_intermediary_steps:
            df.to_csv("STEP_3_tc_with_expanded_columns&rows_NO_conflict.csv")

        # ! I.3.6) return the dataframe in the (data, rows, cols) format
        return (
            df[("info", "data")].values,
            pd.MultiIndex.from_frame(df["inflow"]),  # rows
            pd.MultiIndex.from_frame(df["inflow"]),  # columns
        )

    def __expand_columns(self, df, layer_lvl, layer_key, flow_col=None):
        df_expanded = df[[layer_lvl, layer_key]].pivot(columns=layer_lvl, values=layer_key)
        df_expanded.columns.name = None
        df_expanded = self.autocomplete(df_expanded, np.nan)
        if flow_col:
            df_expanded["flows"] = df[flow_col]
        return df_expanded

    def __replace_all_symbols(self, df, all_symbol):
        for col in self.layer_names[1:]:
            mask = df[col].eq(all_symbol[col]) & df_outflows[col].notna()
            df.loc[mask, col] = df_outflows.loc[mask, col]
        for col in self.layer_names[1:]:
            df[col] = df[col].fillna(all_symbol[col])
        return df

    def __combine_dataframes(self, df_inflows, df_outflows, df):
        other_columns = df.columns.difference(layer_lvls + layer_keys + ["inflows", "outflows"])
        df = pd.concat(
            {
                "inflow": df_inflows,
                "outflow": df_outflows,
                "info": df[other_columns],
            },
            axis=1,
        )
        return df

    def __expand_rows(self, df, layers, fill_idx):
        for layer in layers:
            all_symbol = self.tc_dct["all_symbol"][layer]
            mask = df[("inflow", layer)].eq(all_symbol)
            corresponding_tuples = self.__var["index"][layer].keys()
            temp_data = [corresponding_tuples] * mask.sum()
            temp_idx = mask[mask].index
            new_values = pd.Series(temp_data, index=temp_idx)
            df.loc[mask, ("inflow", layer)] = new_values
            df = df.explode(("inflow", layer))
            mask = df[("outflow", layer)].eq(self.tc_dct["all_symbol"][layer])
            df.loc[mask, ("outflow", layer)] = df.loc[mask, ("inflow", layer)]
        return df

    def __remove_conflicting_rows(self, df):
        priority = pd.IndexSlice[("other", "priority")]
        df = df.sort_values(by=priority, ascending=False)
        df = df[~df.loc[:, ["inflow", "outflow"]].duplicated(keep="first")]
        df = df.sort_index()
        return df

    # ------------------------------------------------------------
    # I.4) Process input data (mass of flows entering the system)
    # ------------------------------------------------------------

    def __read_inflows(self, fill_idx):
        """Read input data from an Excel file and process it.
        Args:
            dct (dict): A dictionary containing the file path, mapper, and sheet information.
            fill_idx (str): The value to fill missing data with.
            year (int, optional): The year to filter the data by. Defaults to None.
        Returns:
            tuple: A tuple containing three arrays: rows, cols, and data.
        """
        # ! I.4.1) read excel file
        filepath = self.inputs_dct["url"]
        sheet = self.inputs_dct["sheet"]
        df = pd.read_excel(filepath, sheet_name=sheet)
        # get the columns correspondance that will ensure consistency
        # (e.g. ["Layer1", "Layer2"] -> ["products", "components"])
        mapper = self.inputs_dct["mapper"]
        df = df.rename(mapper=mapper, axis=1)

        # ! I.4.2) Filter file by year / region
        # ! To be implemented
        # year = None
        # region = None
        # mask_year = df["year"] == year if year else slice(None)
        # mask_region = df["region"] == region if region else slice(None)
        # mask = mask_year & mask_region
        mask = slice(None)

        # ! I.4.3) Expand columns to (F, P, C, M, E) format
        # e.g. [F1, M1, E1] --> [F1, ∅, ∅, M1, E1]
        expanded_df = self.autocomplete(df.loc[mask, :], fill_idx)

        # ! I.4.4) convert excel file into (data, rows) format
        # ! to build the sparse vector Y
        data = df["data"].values
        rows = expanded_df.set_index(list(self.layer_names)).index

        return (data, rows)

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

    def autocomplete(self, df_idx, fill_idx) -> pd.DataFrame:
        """Broadcast partial index into complete index (e.g. [F, M, E] --> [F, ∅, ∅, M, E])
        Args:
            df_idx (pandas.DataFrame): The partial index to be broadcasted.
            fill_idx (int or str): The value to fill the missing columns with.
        Returns:
            numpy.ndarray: The complete index with the missing columns filled.
        """
        if isinstance(df_idx, pd.Series):
            df_idx = df_idx.to_frame()
        missing_cols = list(set(self.layer_names).difference(set(df_idx.columns)))
        new_idx = df_idx.copy()
        new_idx[missing_cols] = np.full(shape=(len(new_idx), len(missing_cols)), fill_value=fill_idx)
        return new_idx.loc[:, list(self.layer_names)]  # Sort columns in the right order

    def compute_row_priority(self, df, nan_symbol):
        """_summary_

        Args:
            serie (pd.Series): _description_
            all_symbol (str): _description_
            nan_symbol (str): _description_

        Returns:
            _type_: _description_
        """

        def compute_cell_priority(serie, all_symbol, nan_symbol):
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

        # build matrix [1, 10, 100, 1_000] for each row
        priority = np.zeros(df.shape[0], dtype=int)
        for i, layer in enumerate(df.columns):
            priority += (
                compute_cell_priority(
                    serie=df[layer],
                    all_symbol=self.tc_dct["all_symbol"][layer],
                    nan_symbol=nan_symbol,
                )
                * 10**i
            )
        return priority

    def get_indexer(self, idxs) -> np.ndarray:
        """Get the integer-based indices corresponding to the given targets.
        Args:
            idxs: The idxs for which to retrieve the indices.
            Possible types are:
                - string (in this case it is assumed that it corresponds to the flow level)
                - tuple[str] / list[str] / np.ndarray[str]
                - nested list / nested tuple / 2d ndarray of strings
                - pd.IndexSlice
        Returns:
            ndarray[int]: The integer-based indices corresponding to the given targets.
        """
        # format targets into appropriate index values
        formatted_idxs = self.format_index(idxs)
        # Convert from 2D-ndarray[str] to 2D-ndarray[int]
        # e.g. ["F0", "P1", "C1", "M2", "E2"] --> [0, 1, 1, 2, 2]
        formatted_idxs_as_int = map_array(arr=formatted_idxs, mapper=self.__var["index"], keys=self.layer_names)
        # Convert from 2D-ndarray[int] to 1D-ndarray[int] using corresponding integer-based indices
        # e.g. [[0, 0, 0, 0, 0]     [0
        #       [0, 0, 0, 0, 1] -->  1
        #       [0, 0, 0, 0, 2]]     2]
        shape = self.index.levshape
        return map_multiidx_to_iloc(arr=formatted_idxs_as_int, shape=shape)

    def format_index(self, idxs) -> np.ndarray:
        """Format index into correct system index

        Args:
            idxs: index to be formatted. Possible types are:
                - string (in this case it is assumed that it corresponds to the flow level)
                - tuple[str] / list[str] / np.ndarray[str]
                - nested list / nested tuple / 2d ndarray of strings
                - pd.IndexSlice

        Returns:
            2d np.ndarray: The formatted index corresponding to the candidates
        """
        if isinstance(idxs, str):
            idxs = (idxs,)
        try:  # this should handle most cases
            formatted_idxs = self.__index.loc[tuple(idxs), :].values
        except KeyError:  # but in case idxs is a nested list/tuple
            idxs = [tuple(row) for row in idxs]
            formatted_idxs = self.__index.loc[idxs, :].values

        if len(formatted_idxs.shape) == 1:
            return formatted_idxs[np.newaxis, :]  # make sure it is 2D
        return formatted_idxs

    def index_iloc(self, keys) -> pd.MultiIndex:
        """Return the index values of the DataFrame at the specified integer-based positions.

        Args:
            keys (Union[int, List[int]]): The integer-based positions.

        Returns:
            pandas.Index: The index values at the specified positions.
        """
        # return self.__index.iloc[keys].index
        return self.__index.iloc[keys].index

    @property
    def var(self) -> dict:
        """Get the variable names of the system.

        Returns:
            dict: The variables of the system.
        """
        return self.__var

    @property
    def flows(self) -> tuple:
        """Get the list of flows within the system.

        Returns:
            tuple: The flows' names.
        """
        return self.__var["flows"]

    @property
    def products(self) -> tuple:
        """Get the list of products within the system.

        Returns:
            tuple: The products' names.
        """
        return self.__var["products"]

    @property
    def components(self) -> tuple:
        """Get the list of components within the system.

        Returns:
            tuple: The components' names.
        """
        return self.__var["components"]

    @property
    def materials(self) -> tuple:
        """Get the list of materials within the system.

        Returns:
            tuple: The materials' names.
        """
        return self.__var["materials"]

    @property
    def elements(self) -> tuple:
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
    def _index(self) -> pd.MultiIndex:
        """Get the index of the system.

        Returns:
            pd.MultiIndex: The index of the system.
        """
        return self.__index

    @property
    def lneqs(self):  # -> scipy.sparse._arrays.csr_array:
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
