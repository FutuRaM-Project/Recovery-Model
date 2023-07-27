from graphviz import Digraph


# set colour map
colour_map = {'element': '#FF4136',
              'compound': '#FF851B',
              'material': '#FFDC00',
              'component': '#2ECC40',
              'product': '#b767f8ff',
              'process': '#0074D9',
              'flow': '#111111',
              'transfer_coefficient': '#AAAAAA',
              'model': '#FFFFFF',
              'note': '#ffff99ff',
              'notetext' : '#000000',
              'titletext': '#000000'}

figure_title = 'Matter classes in the FutuRaM recovery model'
# Create the graph
g = Digraph(name='matter',
            engine='dot')

g.attr('graph',
        label=figure_title,
        labelloc='t',
        fontsize='20',
        fontname='Cabin',
        rankdir='TB',
        splines='ortho',
        nodesep='0.5',
        ranksep='0.5',
        )

# Add a cluster with a background color
with g.subgraph(name='cluster1') as c:
    c.attr(label='Product', style='rounded', bgcolor=colour_map['product'], fontcolor=colour_map['titletext'])
    c.node('examples1', 
           label='- vehicle\n- laptop\n- house\n- heat pump', justify='left',
           shape='note', style='filled', fillcolor=colour_map['note'], fontcolor=colour_map['notetext'])

    # add a subcluster for the components
    with c.subgraph(name='cluster2') as c2:
        c2.attr(label='Component', style='rounded', bgcolor=colour_map['component'])
        c2.node('examples2', label='- catalyst unit\n- circuit board\n- window\n- compressor', shape='note', style='filled', fillcolor=colour_map['note'], fontcolor=colour_map['notetext'])

        # add a subcluster for the materials
        with c2.subgraph(name='cluster3') as c3:
            c3.attr(label='Material', style='rounded', bgcolor=colour_map['material'])
            c3.node('examples3', label='- REE fraction\n- process mass\n- wood\n- non ferrous', shape='note', style='filled', fillcolor=colour_map['note'], fontcolor=colour_map['notetext'])

            # add a subcluster for the compounds
            with c3.subgraph(name='cluster4') as c4:
                c4.attr(label='Compound', style='rounded', bgcolor=colour_map['compound'])
                c4.node('examples4', label='- REE oxides\n- TaO2\n- cellulose\n- Al2O3', shape='note', style='filled', fillcolor=colour_map['note'], fontcolor=colour_map['notetext'])

                # add a subcluster for the elements
                with c4.subgraph(name='cluster5') as c5:
                    c5.attr(label='Element', style='rounded', bgcolor=colour_map['element'])
                    c5.node('examples5', label='- Ce\n- Ta\n- C\n- Al\n', shape='note', style='filled', fillcolor=colour_map['note'], fontcolor=colour_map['notetext'])

    

# Render diagram
g.render(f'../figures/{figure_title.replace(" ","_")}', view=True, format='png')