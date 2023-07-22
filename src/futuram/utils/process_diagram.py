from graphviz import Digraph

from classes.classes_model import Model


def create_process_diagram(model):
    # Create a new Digraph instance
    graph = Digraph()

    # Add nodes for the processes
    for process in model.processes.values():
        graph.node(process.name, shape='box')
    
    # Add edges for the inputs and outputs
    for process in model.processes.values():
        for flow in process.inputs:
            graph.edge(flow.process_from, flow.process_to, label=f"{flow.composition}")

        # for output_substance in process.outputs:
        #     graph.edge(process.name, output_substance.name, label=f"{output_substance.amount} {output_substance.unit}")

    # Set the graph attributes
    graph.attr(rankdir='LR', nodesep='0.6')
    graph.attr(title=f"{model.name} Process Flow Diagram")

    # Render the graph as SVG
    graph.render(f"figures/{model.name}_PFD", format='svg')
    graph.view


if __name__ == "__main__":
    create_process_diagram(model)