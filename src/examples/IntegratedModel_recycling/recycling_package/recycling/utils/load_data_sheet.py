import pandas as pd
import os


def load_data_sheet(filepath, sheet_num):
    """
    Load data from a specific sheet in the Excel file, then save it in the "filename-split" folder as a CSV.
    """
    # Read the data from the Excel file
    data = pd.read_excel(filepath, sheet_name=sheet_num)

    # Extract directory and filename without extension from the filepath
    directory, filename_with_ext = os.path.split(filepath)
    base_filename, _ = os.path.splitext(filename_with_ext)

    # Create a new directory for the CSVs named "filename-split"
    output_dir = os.path.join(directory, f"{base_filename}-split")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the CSV file path
    csv_filepath = os.path.join(output_dir, f"sheet_{sheet_num}.csv")

    # Save the data to CSV
    data.to_csv(csv_filepath, index=False)

    # Load and return data from the CSV for faster operations
    return pd.read_csv(csv_filepath)
    