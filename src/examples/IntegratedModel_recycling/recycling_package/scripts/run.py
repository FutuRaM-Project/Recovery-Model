from core.merge_flows_processes_TCs import merge_data_from_csv

# Paths to your CSV files
flows_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_flows.csv"
processes_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_processes.csv"
tcs_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_recycling\data\ELV_ICE_compositions_flows_processes_TCs-split\ELV_ICE_TCs.csv"

# Call the main function to merge the data
merged_data = merge_data_from_csv(flows_path, processes_path, tcs_path)

# If you want to save the merged data to a CSV file:
output_path = "path_to_save_merged_data.csv"
merged_data.to_csv(output_path, index=False)

print(f"Merged data saved to: {output_path}")
