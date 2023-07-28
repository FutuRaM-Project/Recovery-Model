import os
import logging
import pandas as pd
import graphviz as gv


# Define the configuration settings
config = {
    'data_file': '../data/listOfStocksAndFlows_flowCharts_UID.xlsx',
    'output_folder': '../flowcharts',
    'edge_styles': {
        'compound': {'splines': 'compound'},
        'ortho': {'splines': 'ortho'},
        'curved': {'splines': 'curved'},
        'polyline': {'splines': 'polyline'},
        'line': {'splines': 'line'},
        'spline': {'splines': 'spline'}
    }
}

# Set up the logger
logging.basicConfig(level=logging.INFO, format='** - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_subgraph(g, group, origin, colors, edgestyle):
    """Create a subgraph for a group of nodes and edges."""
    with g.subgraph(name=f'cluster_{origin}') as cc:
        # Add nodes to the subgraph
        for node in set(group['origin level two']).union(set(group['destination level two'])):
            if 'outsideSB' in node:
                cc.node(node, shape='box', style='filled', fillcolor='indianred', penwidth='1.0', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node, fontcolor='black')
            else:
                cc.node(node, shape='box', style='filled', fillcolor='white', penwidth='1.0', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node)

        # Add edges to the graph
        for _, row in group.iterrows():
                if edgestyle == 'splines':
                    if 'outsideSB' in row['destination level two']:
                        cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', fontcolor='red', color="darkred", style='solid', penwidth='2.0', label="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'],arrowsize='0.5')
                    else:
                        cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', label="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'],arrowsize='0.5')
                else:
                    if 'outsideSB' in row['destination level two']:
                        cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', fontcolor='red', color="darkred", style='solid', penwidth='2.0', xlabel="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'],arrowsize='0.5')
                    else:
                        cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', xlabel="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'],arrowsize='0.5')

        # Set cluster attributes
        cc.attr(label=f'{origin}', labelloc='t', labeljust='c', fontname='Cabin', fontsize='18', shape='box', style='rounded', color='black', margin='30,30', bgcolor=colors[origin], penwidth='1.0')

def create_flow_charts():
    """Create flow charts for each edge style."""
    for edgestyle_name, edgestyle_settings in config['edge_styles'].items():
        logger.info(f'Starting to create flow charts for edge style {edgestyle_name}')

        # Create the output folders if they don't exist
        for folder in ['html', 'dot', 'pdf']:
            folder_path = os.path.join(config['output_folder'], edgestyle_name, folder)
            os.makedirs(folder_path, exist_ok=True)

        # Read in the data
        df = pd.read_excel(config['data_file'], sheet_name='Sheet3', header=1, skiprows=0)

        # Group the data by the highest level of the process
        groups = df.groupby('origin level one')
        origins = sorted(list(df['origin level one'].unique()))

        # Loop over the models
        for WS in ['', 'BATT', 'CDW', 'ELV', 'MINW', 'SLASH', 'WEEE', 'SLASH', 'outsideSB']:
            # Filter the data for the current model
            df_ws = df[df["model"].str.contains(WS)]
            models = sorted(list(df_ws.model.unique()))

            # Group the data by the highest level of the process
            origins = sorted(list(df_ws['origin level one'].unique()))

            # Create a directed graph
            g = gv.Digraph()

            # Create a subgraph for each group
            for origin in origins:
                group = df_ws[df_ws['origin level one'] == origin]
                create_subgraph(g, group, origin, colors, edgestyle_settings)

            # Set graph attributes
            g.attr(engine='fdp', concentrate='false')
            g.attr(rankdir='TB', nodesep='0.5', ranksep='1.5', margin='0.2', **edgestyle_settings)
            g.attr(bgcolor='white', penwidth='2.0')
            g.attr(label=f'Flow chart for {WS}: \n including models {models}\n', labelloc='tc', labeljust='c', fontname='Cabin', fontsize='20', shape='box', style='rounded', color='black', margin='0.5,0.5')

            # Save the graph in dot format
            dot_file = os.path.join(config['output_folder'], edgestyle_name, 'dot', f'graphvis_{WS}_{edgestyle_name}.dot')
            g.save(dot_file)

            # Render the graph as a PDF
            pdf_file = os.path.join(config['output_folder'], edgestyle_name, 'pdf', f'graphvis_{WS}_{edgestyle_name}')
            g.render(pdf_file, view=False, cleanup=True, format='pdf')

            # Render the graph as an SVG image
            svg_file = os.path.join(config['output_folder'], edgestyle_name, 'svg', f'graphvis_{WS}_{edgestyle_name}')
            g.render(svg_file, view=False, cleanup=True, format='svg')

            # Create an HTML file with the SVG image
            g.format = 'svg'
            svg_data = g.pipe()
            html_file = os.path.join(config['output_folder'], edgestyle_name, 'html', f'graphvis_{WS}_{edgestyle_name}.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write('<html>\n')
                f.write('<body>\n')
                f.write(f'<img src="data:image/svg+xml;base64,{svg_data.decode()}" />\n')
                f.write('</body>\n')
                f.write('</html>\n')

            logger.info(f'Flow chart for {WS} ({edgestyle_name}) done')

        logger.info(f'All flow charts for edge style {edgestyle_name} done')


if __name__ == '__main__':
    print('\n ****** Starting to create the flow charts ******\n')
    create_flow_charts()
    print('\n ****** Finished creating the flow charts ******\n')