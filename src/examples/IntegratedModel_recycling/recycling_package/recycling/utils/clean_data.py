
def fill_missing_values(merged_df):
    """
    Fill in missing data in the merged dataframe and print warnings if necessary.

    Parameters:
    - merged_df: Merged dataframe.

    Returns:
    - Adjusted dataframe.
    """
    # Handle missing data
    error_message = ""
    if merged_df['consumption_energy_origin'].isnull().any() or merged_df['consumption_energy_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'consumption_energy' column.\n"
        merged_df['consumption_energy_origin'].fillna(1, inplace=True)
        merged_df['consumption_energy_destination'].fillna(1, inplace=True)

    if merged_df['consumption_water_origin'].isnull().any() or merged_df['consumption_water_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'consumption_water' column.\n"
        merged_df['consumption_water_origin'].fillna(2, inplace=True)
        merged_df['consumption_water_destination'].fillna(2, inplace=True)

    if merged_df['cost_operation_origin'].isnull().any() or merged_df['cost_operation_destination'].isnull().any():
        error_message += "WARNING: Empty cells found in 'cost_operation' column.\n"
        merged_df['cost_operation_origin'].fillna(3, inplace=True)
        merged_df['cost_operation_destination'].fillna(3, inplace=True)

    # Step: Populate technology-related columns
    tech_mapping_simple = {}
    reason_mapping_simple = {}
    tlr_mapping_simple = {}

    merged_df['Technology_Used'] = merged_df['process_from'].map(tech_mapping_simple)
    merged_df['Reason_for_Technology_Selection'] = merged_df['process_from'].map(reason_mapping_simple)
    merged_df['TLR'] = merged_df['Technology_Used'].map(tlr_mapping_simple)

    # Step: Add placeholders for scientific references and remarks
    merged_df['Scientific_References'] = ""
    merged_df['Remarks'] = ""

    # Step: Sort the merged dataframe
    merged_df.sort_values(by=['process_from', 'process_to'], inplace=True)

    # Step: Drop empty columns
    keep_columns = ["Technology_Used", "Reason_for_Technology_Selection", "TLR", "Scientific_References", "Remarks"]
    drop_columns = merged_df.columns[merged_df.isnull().all()].tolist()
    drop_columns = [col for col in drop_columns if col not in keep_columns]
    merged_df.drop(columns=drop_columns, inplace=True)
    return merged_df
