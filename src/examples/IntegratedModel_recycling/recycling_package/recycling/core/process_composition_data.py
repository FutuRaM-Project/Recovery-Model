#import pandas as pd
import os
import time
from tqdm import tqdm
from .utils import load_data_sheet, add_average_mass_column, convert_ppm_to_kg_for_materials_and_components, generate_final_format, save_data_to_excel

def process_composition_data(input_file_path, start_year=None, end_year=None):
    """
    Process the provided composition data and generate the final output in the desired format.
    """
    start_time = time.time()  # Start the timer

    # Extract directory and filename without extension from the filepath
    directory, filename_with_ext = os.path.split(input_file_path)
    base_filename, _ = os.path.splitext(filename_with_ext)
    output_dir = os.path.join(directory, f"{base_filename}-split")

    element_names = ['Ag', 'Al', 'Au', 'Cu', 'Dy', 'Fe', 'La', 'Mg', 'Mn', 'Mo', 'Nb', 'Nd', 'Pd', 'Pt', 'Rh', 'Si']
    materials_and_components = [
        'castAluminium', 'wroughtAluminium', 'mildSteel', 'highStrengthSteel', 'castIron', 'magnesium',
        'catalyst', 'EESystem', 'powerElectronics', 'BMS', 'tractionMotorInduction', 'tractionMotorPM'
    ]

    df_kg_original = load_data_sheet(input_file_path, 0)
    df_kg_original = add_average_mass_column(df_kg_original)
    df_kg = df_kg_original.melt(
        id_vars=['time', 'vehicleKey', 'type', 'fuelType', 'engineSize', 'mass', 'average_mass'],
        value_vars=materials_and_components,
        var_name='Material/Component', value_name='kg')

    element_data_kg = {}
    for sheet_num, element_name in tqdm(zip(range(1, 17), element_names), total=len(element_names),
                                        desc="Processing Elements"):
        df_element = load_data_sheet(input_file_path, sheet_num)
        df_element = add_average_mass_column(df_element)

        # Filter the data based on the start and end years
        if start_year:
            df_element = df_element[df_element['time'] >= start_year]
        if end_year:
            df_element = df_element[df_element['time'] <= end_year]

        df_element_kg = convert_ppm_to_kg_for_materials_and_components(df_element, df_kg)
        element_data_kg[element_name] = df_element_kg

    print("Generating final format...")
    final_data = generate_final_format(df_kg_original, element_data_kg, element_names, start_year, end_year)

    print("Saving to Excel files...")
    save_data_to_excel(list(element_data_kg.values()), os.path.join(output_dir, "composition_elements_updated.xlsx"),
                       sheet_names=list(element_data_kg.keys()))
    final_data.to_excel(os.path.join(output_dir, "composition_merged_updated.xlsx"), index=False)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds.")
    