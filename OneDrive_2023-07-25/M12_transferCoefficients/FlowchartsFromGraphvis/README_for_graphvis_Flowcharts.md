# Flow Chart Generator

This Python script allows you to generate a series of flow charts from data stored in an Excel spreadsheet. 

## Table of Contents

- [Flow Chart Generator](#flow-chart-generator)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
  - [FutuRaM\_flowcharts\_graphviz.py](#futuram_flowcharts_graphvizpy)
  - [Dependencies](#dependencies)
  - [Configuration](#configuration)
  - [Function Descriptions](#function-descriptions)


## Usage

To use the script, simply run the Python script from the terminal.


## FutuRaM_flowcharts_graphviz.py

The script reads data from an Excel file (default: '../data/listOfStocksAndFlows_flowCharts_UID.xlsx'), processes it, and generates flow charts, which are then saved in different formats (HTML, dot, PDF, SVG) in the output folder (default: '../flowcharts').

## Dependencies

The script has the following dependencies:

- os
- logging
- pandas
- graphviz


## Configuration

This script uses a configuration dictionary defined at the top of the file to set certain parameters. You can adjust these parameters as needed.

- `data_file`: path to the Excel file containing the data to be plotted.
- `output_folder`: path to the folder where the output files will be saved.
- `edge_styles`: dictionary that defines the styles of the edges in the graph. The keys are the names of the styles, and the values are dictionaries that contain Graphviz attributes for the edges.

## Function Descriptions

There are two main functions in this script:

- `create_subgraph(g, group, origin, colors, edgestyle)`: This function creates a subgraph for a given group of nodes and edges. It takes a Graphviz object `g`, a dataframe `group` that contains the data for the nodes and edges, a string `origin` that represents the highest level of the process, a dictionary `colors` that defines the colors of the nodes, and a dictionary `edgestyle` that contains Graphviz attributes for the edges.

- `create_flow_charts()`: This function generates flow charts for each edge style defined in the configuration dictionary. It reads the data from the Excel file, processes it, and creates a Graphviz object for each system. It then creates subgraphs for each group of nodes and edges, sets graph attributes, and saves the graphs in various formats.
