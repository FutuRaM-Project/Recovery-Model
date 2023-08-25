def convert_ppm_to_kg_for_materials_and_components(df_element, df_kg):
    """
    Convert ppm values to kg for materials and components.
    """
    materials_and_components = [
        'castAluminium', 'wroughtAluminium', 'mildSteel', 'highStrengthSteel', 'castIron', 'magnesium',
        'catalyst', 'EESystem', 'powerElectronics', 'BMS', 'tractionMotorInduction', 'tractionMotorPM'
    ]

    df_element_kg = df_element[['time', 'vehicleKey', 'type', 'fuelType', 'engineSize', 'mass', 'average_mass']].copy()

    for col in materials_and_components:
        # Ensure that the indices match before performing operations
        common_index = df_element.set_index(['time', 'vehicleKey']).index.intersection(
            df_kg[df_kg['Material/Component'] == col].set_index(['time', 'vehicleKey']).index)

        # Filter df_kg based on the current material/component and the time & vehicleKey from df_element
        filtered_kg = df_kg[df_kg['Material/Component'] == col].set_index(['time', 'vehicleKey']).loc[common_index][
            'kg']

        # Multiply the ppm values with the kg values and divide by 1e6 to convert to kg
        df_element_kg[col] = df_element.set_index(['time', 'vehicleKey']).loc[
                                 common_index, col].values * filtered_kg.values / 1e6
        df_element_kg[col] = df_element_kg[col].astype(float)  # Ensure the datatype is float for the new column

    return df_element_kg.reset_index()