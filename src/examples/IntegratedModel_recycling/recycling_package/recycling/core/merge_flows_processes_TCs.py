
from utils.data_integration import integrate_and_merge_data
from utils.handle_coefficients import adjust_transfer_coefficients
from utils.clean_data import fill_missing_values

def merge_data_from_csv(flows_path, processes_path, tcs_path):
    merged_df = integrate_and_merge_data(flows_path, processes_path, tcs_path)
    merged_df = adjust_transfer_coefficients(merged_df)
    merged_df = fill_missing_values(merged_df)
    return merged_df
