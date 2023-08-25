import pandas as pd


def generate_color_mapping(data_df):
    """
    Generate a dynamic color mapping based on unique transformation levels in the dataframe.

    Parameters:
    - data_df (pd.DataFrame): The dataframe containing the transformation levels.

    Returns:
    - dict: A dictionary mapping transformation levels to colors.
    """
    # Define a list of pastel colors for dynamic assignment
    pastel_colors = [
        '#FFD1DC',  # Pastel Pink
        '#B4E1FF',  # Pastel Blue
        '#D1FFD1',  # Pastel Green
        '#FFF5B4',  # Pastel Yellow
        '#FFB4E6',  # Pastel Purple
        '#FFB4B4',  # Pastel Red
        '#D1D1FF',  # Pastel Violet
        '#B4FFB4'  # Pastel Mint
    ]

    # Extract unique transformation levels from both columns
    unique_levels = set(data_df['transformation_level_origin'].unique()).union(
        set(data_df['transformation_level_destination'].unique()))

    # Assign a color to each unique transformation level
    color_map = {}
    for i, level in enumerate(unique_levels):
        color_map[level] = pastel_colors[i % len(pastel_colors)]

    return color_map
