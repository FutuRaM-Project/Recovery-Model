from graphviz import Digraph

# Create a new Digraph object
dot = Digraph()

# Set default graph attributes
dot.attr('graph', fontcolor='black', fontname='Cabin-Medium', fontpath='../utils/Cabin_Medium.ttf', fontsize='30', fontweight='bold', label='Structure of the SRM recovery system model', labelloc='t', penwidth='2', pad='0.4', concentrate='true', bgcolor='white', nodesep='0.6', rankdir='LR')

# Add nodes to the graph

dot.node("Energy", shape='ellipse', style='filled', color='gold', fontcolor='black')

with dot.subgraph(name='cluster_0') as c:
    c.attr(color='black', fontname='Cabin-Medium', fontpath='../utils/Cabin_Medium.ttf', margin='2', padding='4', rankdir='TB', style='rounded', fontsize='20', label='<matters>')
    c.node('matter', color='#2a58adc3', fontcolor='white', height='1.0', shape='ellipse', style='filled', width='2.0', fontsize='18')
    c.node('Element', color='lightblue', fontcolor='black', shape='ellipse', style='filled')
    c.node('Compound', color='lightblue', fontcolor='black', shape='ellipse', style='filled')
    c.node('Material', color='lightblue', fontcolor='black', shape='ellipse', style='filled')
    c.node('Component', color='lightblue', fontcolor='black', shape='ellipse', style='filled')
    c.node('Product', color='lightblue', fontcolor='black', shape='ellipse', style='filled')

with dot.subgraph(name='cluster_1') as c:
    c.attr(color='black', fontname='Cabin-Medium', fontpath='../utils/Cabin_Medium.ttf', margin='2', padding='4', style='rounded', fontsize='20', label='<Processes and Flows>')
    c.node('Flow', color='lightgreen', fontcolor='black', shape='circle', style='filled')
    c.node('Process', color='lightgreen', fontcolor='black', shape='box', style='filled')

with dot.subgraph(name='cluster_2') as c:
    c.attr(color='black', fontname='Cabin-Medium', fontpath='../utils/Cabin_Medium.ttf', margin='10', rankdir='TB', style='rounded', padding='4', fontsize='20', label='<Scenarios and Parameters>')
    c.node('Scenario', color='orange', fontcolor='black', shape='hexagon', style='filled')
    c.node('Parameter', color='orange', fontcolor='black', shape='hexagon', style='filled')

with dot.subgraph(name='cluster_3') as c:
    c.attr(color='black', margin='10', style='rounded', fontsize='20', label='<Impact Assessment Model>')
    c.node('LCA layer', color='#8b13a3', fontcolor='white', height='1', shape='octagon', style='filled')

# Add edges to the graph
dot.edge('Scenario', 'LCA layer', color='orange')
dot.edge('Flow', 'LCA layer', color='green')
dot.edge('Element', 'matter', color='blue')
dot.edge('Compound', 'matter', color='blue')
dot.edge('Material', 'matter', color='blue')
dot.edge('Component', 'matter', color='blue')
dot.edge('Product', 'matter', color='blue')
dot.edge('Element', 'Compound', color='blue')
dot.edge('Element', 'Material', color='blue')
dot.edge('Element', 'Component', color='blue')
dot.edge('Element', 'Product', color='blue')
dot.edge('Compound', 'Material', color='blue')
dot.edge('Compound', 'Component', color='blue')
dot.edge('Compound', 'Product', color='blue')
dot.edge('Material', 'Component', color='blue')
dot.edge('Material', 'Product', color='blue')
dot.edge('Component', 'Product', color='blue')
dot.edge('Flow', 'Process', color='green')
dot.edge('Process', 'Flow', color='green')
dot.edge('matter', 'Flow', color='blue')
dot.edge('Scenario', 'Parameter', color='orange')
dot.edge('Parameter', 'Process', color='orange')
dot.edge('Parameter', 'matter', color='orange')
dot.edge('Parameter', 'Flow', color='orange')
dot.edge('Energy', 'Flow', color='gold')

# Render the graph to a file
dot.render('OverviewOfClassesInTheModel', format='png')
dot.render('OverviewOfClassesInTheModel', format='svg')
dot.render('OverviewOfClassesInTheModel', format='dot')