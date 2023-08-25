import pandas as pd

def save_data_to_excel(data, filepath, sheet_names=None):
    """
    Save data to Excel with specific sheet names.
    """
    with pd.ExcelWriter(filepath) as writer:
        for sheet_name, df in zip(sheet_names, data):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    