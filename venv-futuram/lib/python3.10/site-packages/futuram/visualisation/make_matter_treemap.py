'''
make_matter_treemap.py

This module contains functions for creating treemaps of the matter in a model.

Functions:
- make_matter_treemap(data, name, level=0):  Makes a treemap of the matter in the model.
- prepare_treemap_data(data, parent_key='', level=0): Prepares the data for the treemap.

Dependencies:
- plotly

#! THIS ONE NEEDS WORK: THE NESTED DICTIONARIES SHOULD BE INSIDE OF \
#! THE OUTSIDE DICTIONARY IN THE BOXES. \
#! It would be also be good to have an option to choose the level of nesting to display. 
'''

import os
from math import floor
import plotly.graph_objects as go
from plotly.io import write_html



def prepare_treemap_data(data, parent_key='', level=0):
    """
    Prepares the data for the treemap.
    
    """

    values = []
    labels = []
    visibility = []

    for k, v in data.items():
        new_key = f"{parent_key}/{k}" if parent_key else k

        if isinstance(v, dict):
            child_values, child_labels, child_visibility =\
                  prepare_treemap_data(v, parent_key=new_key, level=level+1)
            values.extend(child_values)
            labels.extend(child_labels)
            visibility.extend(child_visibility)
        else:
            values.append(v)
            labels.append(new_key)
            visibility.append(level)
    
    # vis = []
    # for i in visibility:
    #     if i > 1:
    #         i = i - 2
    #         vis.append(i)
    #     else:
    #         vis.append(i)

    vis = [floor(i/2) for i in visibility]
    visibility = vis
    return values, labels, visibility

def make_matter_treemap(data, name, level=0):
    '''
    Makes a treemap of the matter in the model.
    Uses the plotly package to make a treemap of the matter composition at all levels in the model.

    Args:
        data (dict): A dictionary of the matter composition at all levels in the model.
        name (str): The name of the model.
        level (int): The level of nesting to display.
    
    Returns:
        None
    '''

    print("Under construction")
    return


    # Define the filenames
    if not os.path.exists('../figures'):
        os.makedirs('../figures')

    svg_filename = f'..figures/{name}_treemap.svg'
    html_filename = f'..figures/{name}_treemap.html'

    values, labels, visibility = prepare_treemap_data(data)

    # Create the treemap figure
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[''] * len(labels),
        values=values,
        hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>',
        texttemplate='%{label}',
        visible=True,  # Set the visibility level
        branchvalues='total'
    ))

    # Set the layout properties
    fig.update_layout(
        title='matter Treemap',
        margin=dict(t=50, l=0, r=0, b=0),
        uniformtext=dict(minsize=12, mode='hide')
    )

    # Save the treemap as an SVG file
    fig.write_image(svg_filename)

    # Save the treemap as an HTML file
    write_html(fig, file=html_filename, auto_open=True)

    # Display the treemap
    fig.show()
