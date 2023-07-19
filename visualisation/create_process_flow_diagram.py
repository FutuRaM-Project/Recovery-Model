from graphviz import Digraph
import datetime
import os

# THIS ONE NEEDS NEEDS WORK, in particular the filtering of processes and flows

def create_process_flow_diagram(model, process_filters=None, flow_filters=None, process_tag_filters=None,
                                flow_tag_filters=None, filename_suffix=''):
    """
    Create a process flow diagram using Graphviz and export it as SVG, PNG, and HTML.

    Parameters:
        model (Model): The Model instance containing the objects to visualize.
        process_filters (list): List of process names to include in the diagram. If None, all processes will be included.
        flow_filters (list): List of flow names to include in the diagram. If None, all flows will be included.
        process_tag_filters (list): List of tags to filter processes. Only processes with matching tags will be included.
        flow_tag_filters (list): List of tags to filter flows. Only flows with matching tags will be included.
        filename_suffix (str): The suffix to be added to the filenames. If not provided, a timestamp will be used.
    """
    graph = Digraph()
    graph.attr(rankdir='LR', splines='ortho', nodesep='0.6')

    for process_name, process in model.processes.items():
        if process_filters and process_name not in process_filters:
            continue
        if process_tag_filters and not process.has_tags(process_tag_filters):
            continue

        graph.node(process_name, shape='box')

        for input_flow in process.inputs:
            if flow_filters and input_flow.name not in flow_filters:
                continue
            if flow_tag_filters and not input_flow.has_tags(flow_tag_filters):
                continue

            # substances = input_flow.substances
            # for substance in substances:
            #     substance_name = substance.name
            #     composition = substance.composition
            #     components = ', '.join(component.name for component in composition.get('components', []))
            #     elements = ', '.join(element.symbol for element in composition.get('elements', []))
            #     graph.node(substance_name, shape='ellipse', color='lightblue', fontcolor='black', style='filled',
            #                label=f"{substance_name}\nComponents: {components}\nElements: {elements}")
            #     graph.edge(substance_name, process_name, color='blue')

        for output_flow in process.outputs:
            if flow_filters and output_flow.name not in flow_filters:
                continue
            if flow_tag_filters and not output_flow.has_tags(flow_tag_filters):
                continue

            # substances = output_flow.substances
            # for substance in substances:
            #     substance_name = substance.name
            #     composition = substance.composition
            #     components = ', '.join(component.name for component in composition.get('components', []))
            #     elements = ', '.join(element.symbol for element in composition.get('elements', []))
            #     graph.node(substance_name, shape='ellipse', color='lightblue', fontcolor='black', style='filled',
            #                label=f"{substance_name}\nComponents: {components}\nElements: {elements}")
            #     graph.edge(process_name, substance_name, color='blue')

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename_prefix = f"process_flow_diagram_{timestamp}{filename_suffix}"

    graph.save(filename_prefix + '.dot')
    # graph.save(filename_prefix + '.gv')
    # graph.save(filename_prefix + '.html')
    # graph.save(filename_prefix + '.json')
    graph.save(filename_prefix + '.svg')

    graph.render(filename_prefix, cleanup=True)

    print(f"Process flow diagram saved as {filename_prefix}")
