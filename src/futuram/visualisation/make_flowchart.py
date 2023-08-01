"""
make_flowchart.py

This module contains functions for creating flowcharts of processes and models.

Functions:
- make_flowchart(object):  This is a wrapper function that calls one of the subroutines.
- make_flowchart_process(process): Makes a flowchart of the process.
- make_flowchart_model(model): Makes a flowchart of the model.
- make_flowchart_matter(matter): Makes a flowchart of the matter. 

#! TODO: not yet written

Dependencies:
- graphviz
- os

"""


import os
from graphviz import Digraph

DIR_FIGURES = "../figures/"
DIR_FLOWCHARTS = DIR_FIGURES + "flowcharts"


# TODO: make one for matter also ---> flowchart for each object \and also maybe the graph that Adrien was talking about
def make_flowchart(model_object):
    """
    Creates a flowchart for a model or a process object.
    Depending on the type of object, the appropriate function is called.
    Args:
    object (object): The object to create the flowchart of.
    Outputs:
    A flowchart of the object in the figures folder. Formats: SVG, PDF, PNG and DOT.

    """
    if model_object.type == "process":
        make_flowchart_process(model_object)
    elif model_object.type == "model":
        make_flowchart_model(model_object)
    # elif issubclass(type(object), Matter):
    #     make_flowchart_matter(object)
    #     print(f"Matter flowchart created for: {object.name}")
    else:
        print(f"Object type not supported: {type(model_object)}")
        print("Please provide a Process, Model or Matter object.")
        print(model_object)


def make_flowchart_process(process):
    """
    Creates a flowchart for a process object. 
    Only considers the process itself and its direct inputs and outputs.
    
    Args:
        process (Process): The process object to create the flowchart of.
    Outputs:
        A flowchart of the process in the figures folder. Formats: SVG, PDF, PNG and DOT.
    """
    # Create a new Digraph instance
    graph = Digraph()

    # Set the graph attributes
    graph.attr(
        rankdir="LR",
        nodesep="0.6",
        ranksep="0.6",
        fontname="Cabin",
        fontsize="20",
        #    splines='curved',
        #    overlap='false',
        labelloc="tc",
        labeljust="c",
        label=f"Flowchart (isolated) for: {process.name}\n-----------",
    )

    for flow in list(process.inputs.values()) + list(process.outputs.values()):
        # Add nodes for the inputs and outputs
        graph.node(
            flow.process_to,
            shape="box",
            style="filled",
            fillcolor="lightsalmon1",
            fontname="Cabin",
            fontsize="10",
        )

        graph.node(
            flow.process_from,
            shape="box",
            style="filled",
            fillcolor="darkturquoise",
            fontname="Cabin",
            fontsize="10",
        )

        # Add a node for the process
        graph.node(
            process.name,
            shape="box",
            style="filled",
            fillcolor="mediumorchid1",
            fontname="Cabin",
            fontsize="14",
        )

        # Add edges for the inputs and outputs
        graph.edge(
            flow.process_from,
            flow.process_to,
            label=f"Composition: {flow.composition}\nAmount: {flow.amount:.2e} {flow.unit}",
            fontsize="6",
            fontname="Cabin",
            color="black",
        )

        #    f"Process Flow Diagram for: {process.name}\n-----------", fontsize='20', pos="tc")

    graph.attr(font="Cabin")
    # graph.attr(label=f"{process.description} Process Flow Diagram")

    # Save the graphs in the figures folder
    dir_process_flowcharts = DIR_FLOWCHARTS + "/processes/"

    for _format in ["png", "dot", "svg", "pdf"]:
        dir_process_flowcharts_format = dir_process_flowcharts + _format

        if not os.path.exists(dir_process_flowcharts_format):
            os.makedirs(dir_process_flowcharts_format)

        file_path = dir_process_flowcharts_format + "/" + process.name
        graph.render(file_path, format=_format)

    print(f"\tProcess flowchart created for: {process.name}")
    print(f"\t\t View .pdf @ {os.path.abspath(file_path)}.{_format}")


def make_flowchart_model(
    model, tags=None, ws=None, level=None, name=None, description=None
):
    """
    Creates a flowchart for a model object. 
    Considers all processes in the model and their inputs and outputs.
    Args:
    model (Model): The model object to create the flowchart of.

    tags (list): A list of tags to filter the processes by. Default is None.

    ws (str): The waste stream to filter the processes by. Default is None.

    level (int): The transformation level to filter the processes by. Default is None.
    (examples: 'market', 'component', 'material', 'compound', 'element')

    name (str): The name of the process to filter by. Default is None. 
    (will catch all processes with the string in the name)

    description (str): The description of the process to filter by. Default is None. 
    (will catch all processes with the string in the description)
    
    Outputs:

    A flowchart of the model in the figures folder. 
    Formats: SVG, PDF, PNG and DOT.
        
    """

    # TODO: we should add a way to toggle the display of the processs in the flowchart, maybe with a config file
    # TODO: e.g., highlighting processes that have a high energy consumption, or high OpEx, high emissions, etc.

    print(f"\n\n{'='*90}\n\t Creating flowchart for model: {model.name}\n{'='*90}")
    # Create a new Digraph instance
    graph = Digraph()

    # Set the graph attributes
    graph.attr(
        rankdir="LR",
        nodesep="0.2",
        ranksep="0.3",
        splines="polyline",
        engine="neato",
        fontname="Cabin",
        fontsize="24",
        labelloc="tc",
        labeljust="c",
        label=f"Flowchart for Model: {model.name}\n-----------",
    )

    # Create a set to keep track of processed processes
    added_processes = set()

    # Create a set to keep track of the flows that have already been added
    added_flows = set()

    # Iterate over all processes in the model
    selected_processes = []
    for process in model.processes.values():
        # Check if the process matches the filter criteria
        if (
            (tags is None or set(tags).issubset(process.tags))
            and (ws is None or ws in process.ws)
            and (level is None or process.transformation_level == level)
            and (name is None or name in process.name)
            and (description is None or description in process.description)
        ):
            selected_processes.append(process)

    # Set the cluster divisions
    cluster_names = [
        "other",
        "collection",
        "dismantling",
        "shredding",
        "hammermill",
        "smelter",
        "market",
    ]
    cluster_colormap = {
        "other": "lightgrey",
        "market": "lightpink",
        "collection": "salmon1",
        "dismantling": "plum1",
        "shredding": "darkolivegreen1",
        "hammermill": "darkolivegreen2",
        "smelter": "mediumturquoise",
    }

    cluster_rank = {
        "other": "none",
        "collection": "1",
        "dismantling": "2",
        "shredding": "3",
        "hammermill": "3",
        "smelter": "4",
        "market": "5",
    }

    # Sort the processes into clusters based on the cluster_names
    processes_in_clusters = {}
    for process in selected_processes:
        for cluster_name in cluster_names:
            if cluster_name in process.name.lower():
                processes_in_clusters.setdefault(cluster_name, []).append(process)
            # else:
            #     processes_in_clusters.setdefault('other', []).append(process)

    # Add the clusters to the graph and add the processes to the clusters
    for cluster_name, cluster_processes in processes_in_clusters.items():
        with graph.subgraph(name=cluster_name) as cluster:
            cluster.attr(
                label=cluster_name.capitalize(),
                rankdir="LR",
                fontname="Cabin",
                fontsize="16",
                labelloc="t",
                margin="25",
                style="rounded,filled",
                rank=cluster_rank[cluster_name],
            )

            # Add nodes for processes with cluster_name in the name
            for process in cluster_processes:
                cluster.node(
                    process.name,
                    fontname="Cabin",
                    fontsize="14",
                    shape="box",
                    style="filled",
                    fillcolor=cluster_colormap[cluster_name],
                    tooltip=str(process.to_dict()),
                )

                # Add to the set of processed processes
                added_processes.add(process)

            # Add edges for the inputs and outputs
    for process in selected_processes:
        for flow in process.inputs.values():
            if flow not in added_flows:
                graph.edge(
                    flow.process_from,
                    flow.process_to,
                    label=f"Composition: {flow.composition}\nAmount: {flow.amount:.2e}  {flow.unit}",
                    fontsize="6",
                    fontname="Cabin",
                    color="black",
                    arrowhead="vee",
                    arrowsize="0.4",
                    tooltip=str(flow.to_dict()),
                )
                added_flows.add(flow)

    # annotate the nodes at the end of the process chain
    for process in selected_processes:
        if not process.outputs:
            amount = process.get_total_input_flow()
            if amount is None:
                amount = "x"

            # make an invisible node to attach the annotation to
            graph.node(
                process.name + "_output",
                style="invis",
            )

            graph.edge(
                process.name,
                process.name + "_output",
                label=f"Leaving system boundary: {amount:.2e} {list(process.inputs.values())[0].unit}",
                fontsize="8",
                fontname="Cabin",
                color="darkred",
                fontcolor="darkred",
                arrowhead="rbox",
                style="dashed",
                len="0.25",
                tooltip="This is the amount of material leaving the system boundary.",
            )

    # Save the graphs in the figures folder
    dir_model_flowcharts = DIR_FLOWCHARTS + "/models/"

    if not os.path.exists(dir_model_flowcharts):
        os.makedirs(dir_model_flowcharts)

    for _format in ["png", "dot", "svg", "html","pdf"]:
        dir_model_flowcharts_format = dir_model_flowcharts + _format

        if not os.path.exists(dir_model_flowcharts_format):
            os.makedirs(dir_model_flowcharts_format)

        file_path = dir_model_flowcharts_format + "/" + model.name

        if _format == "html":
            with open(file_path + ".html", "w", encoding="utf-8") as f:
                graph.render(file_path, format="svg")
                f.write("<html><body>\n")
                f.write(f'<img src="{model.name}.svg" title={model.name}>\n')
                f.write("</body></html>\n")

        else:
            graph.render(file_path, format=_format)

    print(f"\t Model flowchart created in figures folder for {model.name}")
    print(f"\tView @ {os.path.abspath(file_path)}.pdf\n")
