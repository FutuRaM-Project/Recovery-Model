# -*- coding: utf-8 -*-
"""

@Author: Adrien Perello / Harmjan de Vries
@Date: 24.03.2024
"""
# %%
import numpy as np
import pandas as pd
import os
from scipy.sparse import coo_array, coo_matrix, eye_array, linalg, csr_array
from typing import Tuple, List
from dataclasses import dataclass
import networkx as nx

# Definition of file/folder names within the overarching data directory
OUTPUT_DATA_FOLDER_NAME = "output_data"
INPUT_DATA_FOLDER_NAME = "input_data"

TCS_FILENAME = "TCs.csv"
INPUTS_FILENAME = "inputs.csv"
COMPOSITION_FILENAME = "composition.csv"
SOLUTION_FILENAME = "solution.csv"


@dataclass
class InputDataFormat:
    """
    Dataclass defining mandatory columns for each input table
    """
    input_columns = ['Stock/Flow ID','Substance_main_parent','Value']
    TCs_columns = ['Input_FlowID','Input_layer','Input_layer_key','Output_FlowID','TC_target_layer','TC_target_key','value']
    composition_columns = ['Stock/ID','Layer 1','Layer 2','Layer 3','Layer 4', 'Value']

    optional_columns = ['Location','Year','Scenario']

    dtypes = {
            'Stock/Flow ID': str,
            'Substance_main_parent': str,
            'Value': float,
            'Input_FlowID': str,
            'Input_layer': str,
            'Input_layer_key': str,
            'Output_FlowID': str,
            'TC_target_layer': str,
            'TC_target_key': str,
            'value': float,
            'Stock/ID': str,
            'Layer 1': str,
            'Layer 2': str,
            'Layer 3': str,
            'Layer 4': str,
            'Location': str,
            'Year': str,
            'Scenario': str,
            'DQS': float,
            'CV': float,
        }


class RecoveryModel:
    """Class representing the recovery model"""
    def __init__(self, data_folder: str, layer_names: List[str]):
        """
        Initialize the System class.
         - Defines and creates folder structure
         - Creates matrices for composition, TC and input data
        Args:
            data_folder: directory containing input and output data for this model
        """
        # Set data folder and create structure if needed
        self.layer_names = layer_names
        self.data_folder = data_folder
        if not os.path.exists(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME)):
            os.makedirs(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME))

        # Read excel files
        self.input_data = self.read_input_data()

    def read_input_data(self) -> dict:
        """
        Read inflows, composition and TCs files and creates the matrices to be used in the model.

        Returns:
            A dictionary with the input inflows, compositions and TCs for each year, scenario and location.
        """
        # Load the input files
        inflows_df = pd.read_csv(
            os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, INPUTS_FILENAME),
            dtype=InputDataFormat.dtypes,
            keep_default_na=False,
            na_values=[]
        )
        composition_df = pd.read_csv(
            os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, COMPOSITION_FILENAME),
            dtype=InputDataFormat.dtypes,
            keep_default_na=False,
            na_values=[]
        )
        tcs_df = pd.read_csv(
            os.path.join(self.data_folder, INPUT_DATA_FOLDER_NAME, TCS_FILENAME),     
            dtype=InputDataFormat.dtypes,
            keep_default_na=False,
            na_values=[]
        )
        layer_names_replace = {item: f"Layer {i+1}" for i, item in enumerate(self.layer_names)}
        tcs_df["Input_layer"] = tcs_df["Input_layer"].replace(layer_names_replace)
        tcs_df["TC_target_layer"] = tcs_df["TC_target_layer"].replace(layer_names_replace)

        # Define the years, locations and scenarios, with the inflows file as the defining basis
        years = inflows_df['Year'].unique() if 'Year' in inflows_df.columns else [None]
        scenarios = inflows_df['Scenario'].unique() if 'Scenario' in inflows_df.columns else [None]
        locations = inflows_df['Location'].unique() if 'Location' in inflows_df.columns else [None]

        input_dfs = []
        for year in years:
            for scenario in scenarios:
                for location in locations:
                    inflows_df_selection = HelperFunctions.select_df_by_year_scenario_location(df=inflows_df, year=year, scenario=scenario, location=location)
                    inflows_df_selection = inflows_df_selection[InputDataFormat.input_columns]
                    tcs_df_selection = HelperFunctions.select_df_by_year_scenario_location(df=tcs_df, year=year, scenario=scenario, location=location)
                    composition_df_selection = HelperFunctions.select_df_by_year_scenario_location(df=composition_df, year=year, scenario=scenario, location=location)

                    inflows_df_selection = inflows_df_selection[InputDataFormat.input_columns]
                    tcs_df_selection = tcs_df_selection[InputDataFormat.TCs_columns]
                    composition_df_selection = composition_df_selection[InputDataFormat.composition_columns]

                    input_dfs.append({
                        "Year":year,
                        "Scenario": scenario,
                        "Location": location,
                        "inflows_df": inflows_df_selection,
                        "composition_df":composition_df_selection,
                        "tcs_df": tcs_df_selection
                    })
        return input_dfs


        # !! not necessary? /  rewrite
        # Create required variables for decoding and encoding the data into sparse matrices.
        # - encoding_dict maps each flow or resource to a unique integer
        # - decoding_dict maps the integer back to the flow or resource
        # - dims is the number of different options for each flow or layer
        # - size is the size of the complete vectors and matrices
        self.decoding_dict = {}
        all_flows = list(set(tcs_df['Input_FlowID']).union(set(tcs_df['Output_FlowID'])))
        self.decoding_dict['Stock/Flow ID'] = dict(enumerate(all_flows))
        for layer_index in range(0,4):
            layer_name = self.layer_names[layer_index]
            layer_unique_resources = ['empty'] + list(set(composition_df['Layer '+str(layer_index+1)].dropna()))
            self.decoding_dict[layer_name] = dict(enumerate(layer_unique_resources))
        self.encoding_dict = {col: {v: k for k, v in dct.items()} for col, dct in self.decoding_dict.items()}
        self.dims = self.get_dims() 
        self.size = np.prod(self.dims, dtype=int)


    def solve_models_and_write_to_output(self) -> pd.DataFrame:
        """
        Solve all entries in the variable self.input_matrices, which contains the model matrices
        for every year, location and scenario. Creates an ouput CSV where the solutions are stored.
        """
        full_solution = pd.DataFrame(columns=["Year","Scenario","Location","Stock/Flow ID","Layer 1","Layer 2","Layer 3","Layer 4","Value"])
        for entry in self.input_data:
            solution = self.solve_model(
                inflows_df=entry["inflows_df"],
                composition_df=entry["composition_df"],
                tcs_df=entry["tcs_df"]
            )
            solution['Year'] = entry['Year']
            solution['Scenario'] = entry['Scenario']
            solution['Location'] = entry['Location']
            full_solution = pd.concat([full_solution, solution],ignore_index=True)

        full_solution = full_solution.sort_values(by=['Year','Scenario', 'Location','Stock/Flow ID', 'Layer 1','Layer 2','Layer 3','Layer 4'])
        full_solution.to_csv(os.path.join(self.data_folder, OUTPUT_DATA_FOLDER_NAME, f"solution.csv"),index=False)
        return full_solution

    def solve_model(self, inflows_df: pd.DataFrame, composition_df: pd.DataFrame, tcs_df: pd.DataFrame) -> pd.DataFrame:
        flows_result = self.create_initial_flows(inflows_df=inflows_df, composition_df=composition_df)

        process_sequence = self.get_process_sequence_from_tcs(tcs_df)
        for _, row in process_sequence.iterrows():
            process_outflow = self.solve_process(tcs_df=tcs_df, flows_result=flows_result, inflow=row["Input_FlowID"], outflow=row["Output_FlowID"])
            process_outflow["Stock/Flow ID"] = row["Output_FlowID"]
            flows_result = pd.concat([flows_result, process_outflow], ignore_index=True)

        # add together the flows
        result = flows_result.groupby(["Stock/Flow ID","Layer 1","Layer 2","Layer 3","Layer 4"],as_index=False).agg({"Value":"sum"})

        return result.replace('empty','')


    def create_initial_flows(self, inflows_df: pd.DataFrame, composition_df: pd.DataFrame) -> pd.DataFrame:
        product_flows = inflows_df[['Stock/Flow ID', 'Substance_main_parent', 'Value']].copy()
        product_flows.rename(columns={'Substance_main_parent': 'Layer 1'}, inplace=True)
        product_flows['Layer 2'] = 'empty'
        product_flows['Layer 3'] = 'empty'
        product_flows['Layer 4'] = 'empty'
        column_order = ['Stock/Flow ID', 'Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Value']
        product_flows = product_flows[column_order]

        composition_df = composition_df[["Stock/ID", "Layer 1","Layer 2","Layer 3","Layer 4", "Value"]].rename(columns={"Stock/ID":"Stock/Flow ID"})
        composition_df[['Layer 1','Layer 2','Layer 3','Layer 4']] = composition_df[['Layer 1','Layer 2','Layer 3','Layer 4']].replace('','empty')
        
        # Apply composition p-c layer
        layer_2_composition = composition_df[(composition_df['Layer 3']=="empty") & (composition_df['Layer 4']=='empty')].copy()
        df_merged = layer_2_composition.merge(product_flows, on=["Stock/Flow ID", "Layer 1"], suffixes=("", "_inflow"))
        df_merged["Value"] = df_merged["Value_inflow"]*df_merged["Value"]
        layer_2_flows = df_merged[["Stock/Flow ID","Layer 1","Layer 2", "Layer 3","Layer 4","Value"]]
        
        # Apply composition c-m layer
        layer_3_composition = composition_df[(composition_df['Layer 3']!="empty") & (composition_df['Layer 4']=='empty')].copy()
        df_merged = layer_3_composition.merge(layer_2_flows, on=["Stock/Flow ID", "Layer 1", "Layer 2"], suffixes=("","_inflow"))
        df_merged["Value"] = df_merged["Value_inflow"]*df_merged["Value"]
        layer_3_flows = df_merged[["Stock/Flow ID","Layer 1","Layer 2", "Layer 3","Layer 4","Value"]]

        # Apply composition m-e layer
        layer_4_composition = composition_df[(composition_df['Layer 3']!="empty") & (composition_df['Layer 4']!='empty')].copy()
        df_merged = layer_4_composition.merge(layer_3_flows, on=["Stock/Flow ID", "Layer 1", "Layer 2", "Layer 3"], suffixes=("","_inflow"))
        df_merged["Value"] = df_merged["Value_inflow"]*df_merged["Value"]
        layer_4_flows = df_merged[["Stock/Flow ID","Layer 1","Layer 2", "Layer 3","Layer 4","Value"]]

        return pd.concat([product_flows, layer_2_flows, layer_3_flows, layer_4_flows], ignore_index=True)

    def solve_process(self, tcs_df: pd.DataFrame, flows_result: pd.DataFrame, inflow: str, outflow: str) -> pd.DataFrame:
        process_inflow = flows_result[flows_result["Stock/Flow ID"]==inflow].drop(columns=["Stock/Flow ID"])
        tcs = tcs_df[(tcs_df["Input_FlowID"]==inflow)&(tcs_df["Output_FlowID"]==outflow)]

        def process_outflow(process_inflow, tcs, input_layer, target_layer):
            if input_layer==target_layer:
                tcs_layer = tcs[(tcs["Input_layer"]==input_layer)&(tcs["TC_target_layer"]==target_layer)][["TC_target_key","value"]]
                tcs_layer.rename(columns={ "TC_target_key": target_layer, "value": "TC"}, inplace=True)
                process_outflow = process_inflow.merge(tcs_layer, on=[target_layer], how='left')
            else:
                tcs_layer = tcs[(tcs["Input_layer"]==input_layer)&(tcs["TC_target_layer"]==target_layer)][["Input_layer_key","TC_target_key","value"]]
                tcs_layer.rename(columns={"Input_layer_key": input_layer, "TC_target_key": target_layer, "value": "TC"}, inplace=True)
                process_outflow = process_inflow.merge(tcs_layer, on=[input_layer, target_layer], how='left')
            process_outflow["TC"].fillna(0, inplace=True)
            process_outflow["Value"] *= process_outflow["TC"]
            return process_outflow[process_outflow["Value"]!=0.0].drop(columns=["TC"])

        process_outflows = []
        for in_layer in ["Layer 1","Layer 2","Layer 3","Layer 4"]:
            for out_layer in ["Layer 1","Layer 2","Layer 3","Layer 4"]:
                process_outflow_iter = process_outflow(process_inflow, tcs, in_layer, out_layer)
                process_outflows.append(process_outflow_iter)

        return pd.concat(process_outflows, ignore_index=True)

    def get_process_sequence_from_tcs(self, tcs_df: pd.DataFrame):
        unique_flow_combinations = tcs_df[['Input_FlowID', 'Output_FlowID']].drop_duplicates()
        
        edges = unique_flow_combinations.apply(lambda row: (row["Input_FlowID"], row["Output_FlowID"]), axis=1).tolist()
        Graph = nx.DiGraph()
        Graph.add_edges_from(edges)
        try:
            node_order = list(nx.topological_sort(Graph))
            node_position = {node: index for index, node in enumerate(node_order)}
            sorted_edges = sorted(edges, key=lambda edge: node_position[edge[0]])
        except nx.NetworkXUnfeasible:
            raise ValueError("The flows in this system cannot be solved as a sequential system: it contains cycles.")

        # Create DataFrame
        process_sequence_df = pd.DataFrame(sorted_edges, columns=['Input_FlowID', 'Output_FlowID'])
        return process_sequence_df



class HelperFunctions:
    @staticmethod
    def is_year_match(year_data, year_target):
        """
        Helper function to subset a dataframe if the year is an exact match or within a range
        Args:
            year_data: Year values that are filled in column. 
            year_target: the instance to be matched

        Returns:
            the matched instances if they exist
        """
        if isinstance(year_data, int):
            return year_data == year_target
        if isinstance(year_data, str):
            if str(year_target) in year_data:
                return True
            if '-' in year_data:
                start, end = map(int, year_data.split('-'))
                return start <= int(year_target) <= end
        return False
    
    @staticmethod
    def select_df_by_year_scenario_location(df: pd.DataFrame, year: str | None, location: str | None, scenario:  str | None) -> pd.DataFrame:

        check_year = 'Year' in df.columns and df['Year'].dropna().astype(bool).any()
        check_scenario = 'Scenario' in df.columns and df['Scenario'].dropna().astype(bool).any()
        check_location = 'Location' in df.columns and df['Location'].dropna().astype(bool).any()
        
        return df.loc[(df['Year'].apply(lambda y: HelperFunctions.is_year_match(y, year)) if check_year else pd.Series(True, index=df.index)) & 
                            (df['Scenario'] == scenario if check_scenario else pd.Series(True, index=df.index)) & 
                            (df['Location'] == location if check_location else pd.Series(True, index=df.index))].drop(columns=['Year','Scenario','Location'], errors='ignore')