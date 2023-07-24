from graphviz import Digraph
import os

from ..classes.processes import Process
from ..classes.model import Model

dir_figures = "../figures/"
dir_flowcharts = dir_figures + "flowcharts"

def make_flowchart(object):
    """
    Creates a flowchart for a model or a process object.
    Depending on the type of object, the appropriate function is called.
    Args:
        object (object): The object to create the flowchart of.
    Outputs:
        Alowchart of the object in the figures folder. Formats: SVG, PDF, PNG and DOT.
    """
    if isinstance(object, Process):
        make_flowchart_process(object)
    elif isinstance(object, Model):
        make_flowchart_model(object)
        print(f"Model flowchart created for: {object.name}")
    # elif issubclass(type(object), Matter):
    #     make_flowchart_matter(object)
    #     print(f"Matter flowchart created for: {object.name}")
    else:
        print(f"Object type not supported: {type(object)}")
        print("Please provide a Process, Model or Matter object.")
        print(object)


def make_flowchart_process(process):
    """
    Creates a flowchart for a process object. Only considers the process itself and its direct inputs and outputs.
    Args:
        process (Process): The process object to create the flowchart of.
    Outputs:
        A flowchart of the process in the figures folder. Formats: SVG, PDF, PNG and DOT.
    """
    # Create a new Digraph instance
    graph = Digraph()

        # Set the graph attributes
    graph.attr(
               rankdir='LR',
               nodesep='0.6',
               ranksep='0.6',
               fontname="Cabin",
               fontsize='20',
            #    splines='curved',
            #    overlap='false',
               labelloc='tc',
               labeljust='c',
               label=f"Flowchart (isolated) for: {process.name}\n-----------")
    

    
    for flow in process.inputs + process.outputs:
    
    # Add nodes for the inputs and outputs
        graph.node(flow.process_to,
                   shape='box',
                   style='filled',
                   fillcolor='lightsalmon1',
                   fontname='Cabin',
                   fontsize='10',
                   )
        
        graph.node(flow.process_from,
                   shape='box',
                   style='filled',
                   fillcolor='darkturquoise',
                   fontname='Cabin',
                   fontsize='10',
                   )
    
    # Add a node for the process
        graph.node(process.name,
                   shape='box',
                   style='filled', 
                   fillcolor='mediumorchid1',
                   fontname='Cabin',
                   fontsize='14',
                   )

    # Add edges for the inputs and outputs
        graph.edge(flow.process_from, flow.process_to,
                   label=f"Composition: {flow.composition}\nAmount: {flow.amount} \nUnit: {flow.unit}",
                    fontsize='6',
                    fontname='Cabin',
                    color='black',
                    )
        
            #    f"Process Flow Diagram for: {process.name}\n-----------", fontsize='20', pos="tc")

    graph.attr(font="Cabin")
    # graph.attr(label=f"{process.description} Process Flow Diagram")

    # Save the graphs in the figures folder
    dir_process_flowcharts = dir_flowcharts + "/processes/"

    for _format in ["png", "dot", "svg", "pdf"]:
        dir_process_flowcharts_format = dir_process_flowcharts + _format

        if not os.path.exists(dir_process_flowcharts_format):
            os.makedirs(dir_process_flowcharts_format)
        
        file_path = dir_process_flowcharts_format+ '/' + process.name
        graph.render(file_path, format=_format)

    print(f"\tProcess flowchart created for: {process.name}")
    print(f"\t\t View .pdf @ {os.path.abspath(file_path)}.{_format}")
    
def make_flowchart_model(model, tags=None, WS=None, level=None, name=None, description=None):
    """
    Creates a flowchart for a model object. Considers all processes in the model and their inputs and outputs.
    Args:
        model (Model): The model object to create the flowchart of.
        tags (list): A list of tags to filter the processes by. Default is None.
        WS (str): The WS to filter the processes by. Default is None.
        level (int): The transformation level to filter the processes by. Default is None. (eg., 'market', 'component', 'material', 'compound', 'element')
        name (str): The name of the process to filter by. Default is None. (will catch all processes with the string in the name)
        description (str): The description of the process to filter by. Default is None. (will catch all processes with the string in the description)
    Outputs:
        A flowchart of the model in the figures folder. Formats: SVG, PDF, PNG and DOT.
    """

#TODO: we should add a way to toggle the display of the processs in the flowchart, maybe with a config file
#TODO: e.g., highlighting processes that have a high energy consumption, or high OpEx, high emissions, etc.

    # Create a new Digraph instance
    graph = Digraph()

    # Set the graph attributes
    graph.attr(
        rankdir='LR',
        nodesep='0.6',
        ranksep='0.6',
        fontname="Cabin",
        fontsize='20',
        labelloc='tc',
        labeljust='c',
        label=f"Flowchart for Model: {model.name}\n-----------",
        )
        

    # Create a set to keep track of processed processes
    processed_processes = set()

    # Iterate over all processes in the model
    for process in model.processes.values():
        # Check if the process matches the filter criteria
        if (tags is None or set(tags).issubset(process.tags)) and \
                (WS is None or WS in process.WS) and \
                (level is None or process.transformation_level == level) and \
                (name is None or name in process.name) and \
                (description is None or description in process.description):

            # Add a node for the process
            if 
            graph.node(process.name,
                       shape='box',
                       style='filled',
                       fillcolor='mediumorchid1',
                       fontname='Cabin',
                       fontsize='14',
                       )
            # Create a new subgraph for processes with "market" in the name
            with graph.subgraph(name='cluster_market') as market:
                market.attr(label='Market Processes', fontname='Cabin', fontsize='16')
                market.attr(style='filled', color='lightblue')
                market.node_attr.update(shape='box', style='filled', fillcolor='lightblue')

                # Add nodes for processes with "market" in the name
                for process in processes:
                    if 'market' in process.name.lower():
                        market.node(process.name, fontname='Cabin', fontsize='14')

            # Add edges for the inputs and outputs
            for flow in process.inputs + process.outputs:
                graph.edge(flow.process_from, flow.process_to,
                           label=f"Composition: {flow.composition}\nAmount: {flow.amount} \nUnit: {flow.unit}",
                           fontsize='6',
                           fontname='Cabin',
                           color='black',
                           )

            # # Add the process to the set of processed processes
            # processed_processes.add(process)

    # 
    # Save the graphs in the figures folder
    dir_model_flowcharts = dir_flowcharts + "/models/"

    if not os.path.exists(dir_model_flowcharts):
        os.makedirs(dir_model_flowcharts)

    for _format in ["png", "dot", "svg", "pdf"]:
        dir_model_flowcharts_format = dir_model_flowcharts + _format

        if not os.path.exists(dir_model_flowcharts_format):
            os.makedirs(dir_model_flowcharts_format)

        file_path = dir_model_flowcharts_format + '/' + model.name
        graph.render(file_path, format=_format)

    print(f"Model flowchart created in figures folder for {model.name}")
    print(f"View .pdf @ {os.path.abspath(file_path)}.pdf")