
def adjust_transfer_coefficients(merged_df):
    """
    Adjust the transfer coefficients to ensure they sum to 1 for each originating process.

    Parameters:
    - merged_df: Merged dataframe.

    Returns:
    - Adjusted dataframe.
    
    # Handle the transfer coefficients to ensure mass balance
    # If there are any missing transfer coefficients, they are filled with a default value of 0.5.
    # The transfer coefficients are then adjusted for each originating process to ensure they sum to 1.
    """
    merged_df['transfer_coefficient'].fillna(0.5, inplace=True)
    for origin in merged_df['process_from'].unique():
        mask = merged_df['process_from'] == origin
        total_tc = merged_df.loc[mask, 'transfer_coefficient'].sum()
        if total_tc != 0:
            merged_df.loc[mask, 'transfer_coefficient'] /= total_tc
            
            
            
    # Based on the adjusted transfer coefficients, low and high limits are calculated.        
    merged_df['low_transfer_coefficient'] = merged_df['transfer_coefficient'] * 0.9
    merged_df['high_transfer_coefficient'] = merged_df['transfer_coefficient'] * 1.1
    return merged_df
