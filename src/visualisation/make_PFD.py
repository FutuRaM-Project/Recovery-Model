from graphviz import Digraph

def create_process_diagram(process):
    # Create a new Digraph instance
    graph = Digraph()

    graph.node(process.name, shape='box')
    # Add nodes for the inputs and outputs
    for substance in process.inputs + process.outputs:
        graph.node(substance.name)

    # Add edges for the inputs and outputs
    for input_substance in process.inputs:
        graph.edge(input_substance.name, process.name, label=f"{input_substance.amount} {input_substance.unit}")

    for output_substance in process.outputs:
        graph.edge(process.name, output_substance.name, label=f"{output_substance.amount} {output_substance.unit}")

    # Set the graph attributes
    graph.attr(rankdir='LR', nodesep='0.6')
    graph.attr(title=f"{process.name} Process Flow Diagram")
    graph.attr(label=f"{process.description} Process Flow Diagram")

    # Render the graph as SVG
    graph.render(f"figures/{process.name}_PFD", format='svg')
    graph.view
