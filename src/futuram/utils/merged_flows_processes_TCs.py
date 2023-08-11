import pandas as pd
def merge_data(flows_path, processes_path, tcs_path):
    """
    This function merges flows, processes, and transfer coefficients data to provide a comprehensive dataset.
    Parameters:
    - flows_path: Path to the flows dataset.
    - processes_path: Path to the processes dataset.
    - tcs_path: Path to the transfer coefficients dataset.

    Returns:
    - merged_df: A dataframe consisting of merged data.
    """

    # Step 1: Load the datasets
    flows_df = pd.read_excel(flows_path)
    processes_df = pd.read_excel(processes_path)
    tcs_df = pd.read_excel(tcs_path)

    # Step 2: Merge the datasets
    # The datasets are merged on the basis of the processes involved.
    # Here, data from the processes dataset is added to the flows dataset for both the originating and destination processes.
    # Next, the transfer coefficients data is merged based on the flow of materials from one process to another.
    merged_df = flows_df.merge(
        processes_df, left_on='process_from', right_on='name', how='left'
    ).merge(
        processes_df, left_on='process_to', right_on='name', how='left', suffixes=('_origin', '_destination')
    ).merge(
        tcs_df, left_on=['process_from', 'process_to'], right_on=['flow_input', 'flow_output'], how='left'
    )

    # Step 3: Handle the transfer coefficients to ensure mass balance
    # If there are any missing transfer coefficients, they are filled with a default value of 0.5.
    # The transfer coefficients are then adjusted for each originating process to ensure they sum to 1.
    merged_df['transfer_coefficient'].fillna(0.5, inplace=True)
    for origin in merged_df['process_from'].unique():
        mask = merged_df['process_from'] == origin
        total_tc = merged_df.loc[mask, 'transfer_coefficient'].sum()
        if total_tc != 0:
            merged_df.loc[mask, 'transfer_coefficient'] /= total_tc

    # Based on the adjusted transfer coefficients, low and high limits are calculated.
    merged_df['low_transfer_coefficient'] = merged_df['transfer_coefficient'] * 0.9
    merged_df['high_transfer_coefficient'] = merged_df['transfer_coefficient'] * 1.1

    # Step 4: Handle missing data and print warnings
    # This step checks for missing data in specific columns.
    # It not only fills the missing data with default values but also prints a warning to notify the user.
    error_message = ""
    if merged_df['consumption_energy_origin'].isnull().any() or merged_df[
        'consumption_energy_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'consumption_energy' column in the file {}\n".format(flows_path)
        merged_df['consumption_energy_origin'].fillna(1, inplace=True)
        merged_df['consumption_energy_destination'].fillna(1, inplace=True)

    if merged_df['consumption_water_origin'].isnull().any() or merged_df[
        'consumption_water_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'consumption_water' column in the file {}\n".format(flows_path)
        merged_df['consumption_water_origin'].fillna(2, inplace=True)
        merged_df['consumption_water_destination'].fillna(2, inplace=True)

    if merged_df['cost_operation_origin'].isnull().any() or merged_df['cost_operation_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'cost_operation' column in the file {}\n".format(flows_path)
        merged_df['cost_operation_origin'].fillna(3, inplace=True)
        merged_df['cost_operation_destination'].fillna(3, inplace=True)

    # Print the error message if there are discrepancies found.
    if error_message:
        print("ERROR: Found discrepancies in the input files!")
        print(error_message)
        print(
            "Assumed default values for empty cells: 1 for 'consumption_energy', 2 for 'consumption_water', and 3 for 'cost_operation'.")

    # Step 5: Populate technology-related columns
    # Here, mappings are created to map technology details to the originating processes.
    tech_mapping_simple = {}
    reason_mapping_simple = {}
    tlr_mapping_simple = {}

    merged_df['Technology_Used'] = merged_df['process_from'].map(tech_mapping_simple)
    merged_df['Reason_for_Technology_Selection'] = merged_df['process_from'].map(reason_mapping_simple)
    merged_df['TLR'] = merged_df['Technology_Used'].map(tlr_mapping_simple)

    # Check for incorrect values in technology-related columns and print warnings.
    if merged_df['Technology_Used'].isnull().any() or merged_df['Technology_Used'].apply(
            lambda x: isinstance(x, (int, float))).any():
        print("ERROR: Incorrect values found in 'Technology_Used' column in the file {}".format(flows_path))

    if merged_df['Reason_for_Technology_Selection'].isnull().any() or merged_df[
        'Reason_for_Technology_Selection'].apply(lambda x: isinstance(x, (int, float))).any():
        print("ERROR: Incorrect values found in 'Reason_for_Technology_Selection' column in the file {}".format(
            flows_path))

    if merged_df['TLR'].isnull().any() or merged_df['TLR'].apply(lambda x: isinstance(x, str)).any():
        print("ERROR: Incorrect values found in 'TLR' column in the file {}".format(flows_path))

    # Step 6: Add placeholders for scientific references and remarks
    # These columns are initialized with empty strings.
    merged_df['Scientific_References'] = ""
    merged_df['Remarks'] = ""

    # Step 7: Sort the merged dataframe for better readability
    merged_df.sort_values(by=['process_from', 'process_to'], inplace=True)

    return merged_df