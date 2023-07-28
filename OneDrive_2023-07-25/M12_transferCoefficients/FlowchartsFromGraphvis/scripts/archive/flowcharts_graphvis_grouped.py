import os
import pandas as pd
import graphviz as gv


# wrap the code in a loop over the edge styles
edgestyles = ['compound', 'ortho', 'curved', 'polyline', 'line', 'spline']

print('\n ****** Starting to create the flow charts ******\n')
for edgestyle in edgestyles:
        
    # Define the folder names
    folders = ['html', 'dot', 'pdf']

    # Create the folders if they don't exist
    for folder in folders:
        if not os.path.exists(f'../flowcharts/{edgestyle}/{folder}'):
            os.makedirs(f'../flowcharts/{edgestyle}/{folder}')


    # Read in the data
    df = pd.read_excel('../data/listOfStocksAndFlows_flowCharts_UID.xlsx', sheet_name='Sheet3', header=1, skiprows=0)
    df.columns

    # group the data by the highest level of the process (eg. 'collection', 'production', 'disposal')
    groups = df.groupby('origin level one')
    origins = sorted(list(df['origin level one'].unique()))
    # Define the colors for each group
    colors = {
        'collection': 'orchid',
        'mechanical recovery processes': 'tan',
        'preparation for reuse': 'palevioletred2',
        'production': 'lightskyblue',
        'distribution and usage': 'lightgoldenrod',
        'thermal recovery processes': 'lightcyan',
        'chemical recovery processes': 'lightcoral',
        'outsideSB': 'gray43',
        'disposal processes': 'lightseagreen',
        'production / thermal recovery processes': 'lightsalmon',
        'biological/thermal/chemical recovery processes': 'lightsteelblue'
    }

    df.head()
    list(df.columns)

    # Get the unique models for grouping the nodes or filtering for a less complex graph based on the model name (WS)
    models = sorted(list(df.model.unique()))

    WSs = ['', 'BATT','CDW','ELV','MINW' , 'SLASH', 'WEEE', 'SLASH', 'outsideSB']

    # loop over the models
    for WS in WSs:
        # Filter the data for the current model
        df_ws = df[df["model"].str.contains(WS)]
        models = sorted(list(df_ws.model.unique()))

        # group the data by the highest level of the process (eg. 'collection', 'production', 'disposal')
        origins = sorted(list(df_ws['origin level one'].unique()))

        # Create a directed graph
        g = gv.Digraph()
        
        # create a subgraph for the whole graph to get a border around the whole graph
        # with g.subgraph(name='cluster') as c:

        # Create a subgraph for each group
        for origin in origins:
            group = df_ws[df_ws['origin level one'] == origin]
            with g.subgraph(name=f'cluster_{origin}') as cc:
                # Add nodes to the subgraph
                for node in set(group['origin level two']).union(set(group['destination level two'])):
                    if 'outsideSB' in node:
                        cc.node(node, shape='box', style='filled', fillcolor='white', penwidth='2.0', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node, fontcolor='black')
                    else:
                        cc.node(node, shape='box', style='filled', fillcolor='white', penwidth='2.0', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node)

                # Add edges to the graph
                for _, row in group.iterrows():
                    if edgestyle == 'splines':
                        if 'outsideSB' in row['destination level two']:
                            cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', fontcolor='red', color="firebrick3", style='dotted', penwidth='2.0', label="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'])
                        else:
                            cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', label="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'])
                    else:
                        if 'outsideSB' in row['destination level two']:
                            cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', fontcolor='red', color="firebrick3", style='dotted', penwidth='2.0', xlabel="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'])
                        else:
                            cc.edge(row['origin level two'], row['destination level two'], fontname='Cabin', fontsize='4', xlabel="\n".join(row['stocks and flows (unique name in flow chart)'].split("_")), tooltip=row['stocks and flows (unique name in flow chart)'])

                    # Set cluster attributes
                cc.attr(label=f'{origin}', labelloc='t', labeljust='c', fontname='Cabin', fontsize='18', shape='box', style='rounded', color='black', margin='30,30', bgcolor=colors[origin], penwidth='1.0')


            # set supercluster attributes
            # c.attr(style='rounded', penwidth='1.0', bgcolor='white')



    ## GENERAL ATTRIBUTES FOR THE GRAPH STYLING
        
        # Set graph attributes
        g.attr(engine='fdp', concentrate='false')
        g.attr(rankdir='TB', nodesep='0.5', ranksep='1.5', margin='0.2', splines=edgestyle)
        g.attr(bgcolor='white', penwidth='2.0')
        g.attr(label=f'Flow chart for {WS}: \n including models {models}\n', labelloc='tc', labeljust='c', fontname='Cabin', fontsize='20', shape='box', style='rounded', color='black', margin='0.5,0.5')


    ## SAVE THE GRAPH IN DIFFERENT FORMATS

        # Save the graph in dot format
        g.save(f'../flowcharts/{edgestyle}/dot/graphvis_{WS}_{edgestyle}.dot')
        # Render the graph as a PDF
        g.render(f'../flowcharts/{edgestyle}/pdf/graphvis_{WS}_{edgestyle}', view=False, cleanup=True, format='pdf')
        # Render the graph as an SVG image
        g.render(f'../flowcharts/{edgestyle}/svg/graphvis_{WS}_{edgestyle}', view=False, cleanup=True, format='svg')
        
        # Create an HTML file with the SVG image
        g.format = 'svg'
        svg_data = g.pipe()
        with open(f'../flowcharts/{edgestyle}/html/graphvis_{WS}_{edgestyle}.html', 'w', encoding='utf-8') as f:
            f.write('<html>\n')
            f.write('<body>\n')
            f.write(f'<img src="data:image/svg+xml;base64,{svg_data.decode()}" />\n')
            f.write('</body>\n')
            f.write('</html>\n')
        
        print(f'Flow chart for {WS} ({edgestyle}) done')

print('\n ****** All flow charts done ******\n')

