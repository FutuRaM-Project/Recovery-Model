# PART 1: Merging Data from CSV Files

# Step 1: Install and import necessary packages
# pip install pandas
# import pandas as pd
from merge_and_split_main.main_functions import merge_data_from_csv

# Step 2: Define the paths to your CSV files
flows_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_flows.csv"
processes_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_processes.csv"
tcs_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_TCs.csv"

# Step 3: Call the main function to merge the data
merged_data = merge_data_from_csv(flows_path, processes_path, tcs_path)

# Step 4: Save the merged data to a desired CSV file
output_path = "path_to_save_merged_data.csv"
merged_data.to_csv(output_path, index=False)
print(f"Merged data saved to: {output_path}")


# PART 2: DOT flowchart with TCs
# Step 1: Setup and Imports
# import os
from utils import create_dynamic_colored_dot_flowchart

# Step 2: Specify Input and Output Directories
input_file_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\Merged_flows_processes_TCs.csv"
output_dir = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\visualization"

# Step 3: Generate DOT File
dot_file_path = create_dynamic_colored_dot_flowchart(input_file_path, output_dir)

# Step 4: Confirmation
print(f"DOT representation saved to {dot_file_path}")



# PART 3: Processing Composition Data

# Step 1: Install and import necessary packages
pip install recycling
from recycling.core import process_composition_data

# Step 2: Define the input path and time range for processing
input_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_ELV\src\examples\ELV\data\Stock_model\composition.xlsx"
start_year = 1980  # Specify the start year here
end_year = 2023    # Specify the end year here

# Step 3: Process the composition data
process_composition_data(input_path, start_year, end_year)