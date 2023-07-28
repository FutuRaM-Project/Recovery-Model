import os
import pandas as pd
import graphviz as gv

# make folder for the html files
if not os.path.exists('../flowcharts/html'):
    os.makedirs('../flowcharts/html')
# make folder for the dot files
if not os.path.exists('../flowcharts/dot'):
    os.makedirs('../flowcharts/dot')
# make folder for the pdf files
if not os.path.exists('../flowcharts/pdf'):
    os.makedirs('../flowcharts/pdf')


# Read in the data
df = pd.read_excel('../data/listOfStocksAndFlows_flowCharts_UID.xlsx', sheet_name='Sheet3', header=1, skiprows=0)

df.head()

# Get the unique models for grouping the nodes or filtering for a less complex graph
list(df.columns)
sorted(list(df.model.unique()))

WSs = ['', 'BATT','CDW','ELV','MINW' , 'SLASH', 'WEEE', 'SLASH', 'outsideSB']

# loop over the models
for WS in WSs:
    # Filter the data for the current model
    df_ws = df[df["model"].str.contains(WS)]
    # print(WS , ":" , len(df_ws))

    # Get the unique values of the 'model' column
    models = list(df_ws["model"].unique())

    # Create a directed graph
    g = gv.Digraph()
    
    with g.subgraph(name='cluster') as c:
    # Add nodes to the graph
        for node in set(df_ws['origin level two']).union(set(df_ws['destination level two'])):
            if 'outsideSB' in node:
                c.node(node, shape='box', style='filled', color='lightpink', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node, fontcolor='black')
            else:
                c.node(node, shape='box', style='filled', color='lightblue', fontname='Cabin', fontsize='10', margin='0.1,0.1', width='0.1', height='0.1', fixedsize='false', tooltip=node)


        # Add edges to the graph
        for _, row in df_ws.iterrows():
            if 'outsideSB' in row['destination level two']:
                c.edge(row['origin level two'], row['destination level two'], label=(row['stocks and flows (unique name in flow chart)']+" (outsideSB)"), fontname='Arial', fontsize='8', fontcolor='red', color='red', style='dotted')
            else:
                c.edge(row['origin level two'], row['destination level two'], label=row['stocks and flows (unique name in flow chart)'], fontname='Cabin', fontsize='8')

            # Set cluster attributes
            # c.attr(label=f'Flow chart for {WS}: \n including models {models}\n')
        c.attr(style='rounded', penwidth='1.0', bgcolor='white')
    
    # Set graph attributes
    g.attr(rankdir='LR', nodesep='0.5', ranksep='0.5', margin='0.2')
    g.attr(bgcolor='white', penwidth='2.0')
    g.attr(label=f'Flow chart for {WS}: \n including models {models}\n', labelloc='tc', labeljust='c', fontname='Cabin', fontsize='20', shape='box', style='rounded', color='black', margin='0.5,0.5')

    # Save the graph in dot format
    g.save(f'../flowcharts/dot/graphvis_{WS}.dot')
    # Render the graph as a PDF
    g.render(f'../flowcharts/pdf/graphvis_{WS}', view=False, cleanup=True, format='pdf')


    # Render the graph as an HTML file with tooltips
# Render the graph as an SVG image
    g.format = 'svg'
    svg_data = g.pipe()

    # Create an HTML file with the SVG image
    with open(f'../flowcharts/html/graphvis_{WS}.html', 'w') as f:
        f.write('<html>\n')
        f.write('<body>\n')
        f.write(f'<img src="data:image/svg+xml;base64,{svg_data.decode()}" />\n')
        f.write('</body>\n')
        f.write('</html>\n')
    
    print(f'Flow chart for {WS} done')