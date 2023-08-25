def add_average_mass_column(df):
    """
    Add an 'average_mass' column to the DataFrame.
    """
    # Convert the 'mass' column to string for processing and remove 'kg'
    df['mass'] = df['mass'].str.replace('kg', '').str.strip().astype(str)

    # Compute the average mass based on conditions and store in the 'average_mass' column
    df['average_mass'] = df['mass'].apply(
        lambda x: 1280 if x.lower() == 'unknown' else
                  (1000 if '<1000' in x else
                   (1500 if '>1500' in x else
                    float(sum(map(int, x.split('-'))) / 2) if '-' in x else float(x))))
    return df