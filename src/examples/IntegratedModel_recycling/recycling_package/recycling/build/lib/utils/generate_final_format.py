def generate_final_format(df_kg, element_data_kg, element_names, start_year=None, end_year=None):
    """
    Generates a DataFrame in the final desired format with additional columns and modified order.
    """
    materials = ['castAluminium', 'wroughtAluminium', 'mildSteel', 'highStrengthSteel', 'castIron', 'magnesium']
    components = ['catalyst', 'EESystem', 'powerElectronics', 'BMS', 'tractionMotorInduction', 'tractionMotorPM']
    all_data = []

    years_to_consider = df_kg['time'].unique()

    # Filter the years based on start and end years if provided
    if start_year:
        years_to_consider = [year for year in years_to_consider if year >= start_year]
    if end_year:
        years_to_consider = [year for year in years_to_consider if year <= end_year]

    for year in years_to_consider:
        for material_or_component in materials + components:
            for vehicle_key in df_kg['vehicleKey'].unique():
                row_data = {}
                base_data = df_kg[(df_kg['time'] == year) & (df_kg['vehicleKey'] == vehicle_key)].iloc[0]
                row_data['vehicleKey'] = base_data['vehicleKey']
                row_data['type'] = base_data['type']
                row_data['fuelType'] = base_data['fuelType']
                row_data['engineSize'] = base_data['engineSize']
                row_data['mass'] = base_data['mass']
                row_data['average_mass'] = base_data['average_mass']
                row_data['year'] = year
                row_data['component'] = material_or_component
                for element_name in element_names:
                    current_data = element_data_kg[element_name]
                    filtered_data = current_data[(current_data['time'] == year) & (current_data['vehicleKey'] == vehicle_key)]
                    row_data[element_name] = filtered_data[material_or_component].values[0] if not filtered_data.empty else 0
                all_data.append(row_data)

    final_df = pd.DataFrame(all_data)
    final_df.insert(0, 'serial_number', range(1, 1 + len(final_df)))
    return final_df