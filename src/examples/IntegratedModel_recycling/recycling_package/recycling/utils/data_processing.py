
import pandas as pd

def integrate_and_merge_data(flows_path, processes_path, tcs_path):
    """
    Load the datasets from the provided paths.

    Parameters:
    - flows_path: Path to the flows dataset CSV.
    - processes_path: Path to the processes dataset CSV.
    - tcs_path: Path to the transfer coefficients dataset CSV.

    """
    # Load data
    flows_df = pd.read_csv(flows_path)
    processes_df = pd.read_csv(processes_path)
    tcs_df = pd.read_csv(tcs_path)
    
    """
    Merge the flows, processes, and transfer coefficients datasets.

    Returns:
    - Merged dataframe.
    
    # The datasets are merged on the basis of the processes involved.
    # Here, data from the processes dataset is added to the flows dataset for both the originating and destination processes.
    """
    
    # Merge data
    merged_df = flows_df.merge(
        processes_df, left_on='process_from', right_on='name', how='left'
    ).merge(
        processes_df, left_on='process_to', right_on='name', how='left', suffixes=('_origin', '_destination')
    ).merge(
        tcs_df, left_on=['process_from', 'process_to'], right_on=['flow_input', 'flow_output'], how='left'
    )
    return merged_df
