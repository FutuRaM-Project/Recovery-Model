import pandas as pd
import os
from .data_processing import generate_color_mapping


def create_dynamic_colored_dot_flowchart(input_path: str, output_directory: str) -> str:
    """
    Generate a DOT representation of the material flow with colored nodes based on dynamic transformation levels.

    Parameters:
    - input_path (str): Path to the input CSV file.
    - output_directory (str): Directory where the DOT file should be saved.

    Returns:
    - str: Path to the generated DOT file.
    """

    # Load the data
    data_df = pd.read_csv(input_path)

    # Generate a dynamic color mapping based on the data
    color_mapping = generate_color_mapping(data_df)

    # Filter the required columns
    filtered_df = data_df[['process_from', 'description_origin', 'transformation_level_origin',
                           'process_to', 'description_destination', 'transformation_level_destination',
                           'transfer_coefficient']]

    # Begin DOT representation for the linear flowchart
    dot_representation = "digraph G {\n"
    dot_representation += "rankdir=LR;\n"
    dot_representation += "node [shape=box];\n"

    # Track nodes we've already added
    added_nodes = set()
    for _, row in filtered_df.iterrows():
        origin = row['process_from']
        destination = row['process_to']
        coefficient = row['transfer_coefficient']
        description_from = row['description_origin']
        description_to = row['description_destination']
        origin_color = color_mapping.get(row['transformation_level_origin'], '#FFFFFF')
        destination_color = color_mapping.get(row['transformation_level_destination'], '#FFFFFF')

        # Add nodes with descriptions as labels and colors based on transformation levels
        if origin not in added_nodes:
            dot_representation += f'"{origin}" [label="{description_from}", fillcolor="{origin_color}", style="filled"];\n'
            added_nodes.add(origin)
        if destination not in added_nodes:
            dot_representation += f'"{destination}" [label="{description_to}", fillcolor="{destination_color}", style="filled"];\n'
            added_nodes.add(destination)

        # Add edge with transfer coefficient as label
        dot_representation += f'"{origin}" -> "{destination}" [label="{coefficient:.2f}%"];\n'

    # Add legend for the transformation levels
    dot_representation += "{\n"
    dot_representation += "rank = sink;\n"
    dot_representation += 'node [shape=box, style="filled"];\n'
    for level, color in color_mapping.items():
        dot_representation += f'legend_{level} [label="{level}", fillcolor="{color}"];\n'
    dot_representation += "}\n"

    dot_representation += "}"

    # Determine the output DOT file path
    file_name = os.path.splitext(os.path.basename(input_path))[0] + "_dynamic_colored.dot"
    output_path = os.path.join(output_directory, file_name)

    # Save the DOT representation
    with open(output_path, "w") as file:
        file.write(dot_representation)

    return output_path
