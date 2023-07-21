from graphviz import Digraph

def make_PFD(process):
    # Create a new Digraph instance
    graph = Digraph()

    graph.node(process.name, shape='box')
    # Add nodes for the inputs and outputs
    for matter in process.inputs + process.outputs:
        graph.node(matter.name)

    # Add edges for the inputs and outputs
    for input_matter in process.inputs:
        graph.edge(input_matter.name, process.name, label=f"{input_matter.amount} {input_matter.unit}")

    for output_matter in process.outputs:
        graph.edge(process.name, output_matter.name, label=f"{output_matter.amount} {output_matter.unit}")

    # Set the graph attributes
    graph.attr(rankdir='LR', nodesep='0.6')
    graph.attr(title=f"{process.name} Process Flow Diagram")
    graph.attr(label=f"{process.description} Process Flow Diagram")

    # Render the graph as SVG
    graph.render(f"figures/{process.name}_PFD", format='svg')
    graph.view
