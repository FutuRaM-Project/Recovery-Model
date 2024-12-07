'''
processes.py

This module contains the Process class.

Classes:
    Process

Dependencies:
    tabulate
    prettytable
    ../visualisation/make_flowchart.py
'''

from tabulate import tabulate
from prettytable import PrettyTable

from ..visualisation import make_flowchart


class Process:
    """
    A class representing a process that transforms input flows into output flows.

    Attributes:
        name (str): The name of the process.
        description (str): A description of the process.
        tags (list): A list of tags associated with the process.
        WS (list): A list of waste streams associated with the process.
        inputs (list): A list of input flows to the process.
        outputs (list): A list of output flows from the process.
        parameters (list): A list of parameters associated with the process.
    """

    def __init__(self, name):
        self.name = name
        self.type = "process"
        self.uuid = None
        self.description = None
        self.tags = []
        self.transformation_level = None
        self.WS = None
        self.consumption_energy = None
        self.consumption_water = None
        self.cost_operation = None
        self.cost_capital = None
        self.transfer_coefficients = {}
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}

    def print_transfer_coefficients(self):
        """
        Prints the transfer coefficients of the process in a nice table
        """
        if self.to_dict()["transformation_level"] == "market":
            print(f"{self.name}: Market processes don't have transfer coefficients.")
            return

        print(
            f'\n{"-"*60}\n\t  Transfer coefficients of process: {self.name}\n{"-"*60}'
        )

        # Create combined table
        combined_table = PrettyTable()
        combined_table.field_names = [
            "Input",
            "Output",
            "Transfer coefficient",
            "Uncertainty",
        ]
        for tc in self.transfer_coefficients.values():
            tc_value = f'{tc["transfer_coefficient"]:.2f}'
            combined_table.add_row(
                [tc["input"], tc["output"], tc_value, tc["uncertainty"]]
            )

        # Print combined table
        print(combined_table)

    def print_flows(self):
        """
        Prints the input and output flows of the process in a nice table
        """
        print(f'\n{"-"*60}\n\t  Flows of process: {self.name}\n{"-"*60}')

        # Create combined table
        combined_table = PrettyTable()
        combined_table.field_names = [
            "Type",
            "Name",
            "From",
            "To",
            "Composition",
            "Amount",
            "Unit",
            "Tags",
        ]
        for flow in self.inputs.values():
            combined_table.add_row(
                [
                    "Input",
                    flow.name,
                    flow.process_from,
                    flow.process_to,
                    flow.composition,
                    flow.amount,
                    flow.unit,
                    flow.tags,
                ]
            )
        # Add empty row to separate inputs and outputs
        if self.inputs and self.outputs:
            combined_table.add_row(["", "", "", "", "", "", "", ""])
        for flow in self.outputs.values():
            combined_table.add_row(
                [
                    "Output",
                    flow.name,
                    flow.process_from,
                    flow.process_to,
                    flow.composition,
                    flow.amount,
                    flow.unit,
                    flow.tags,
                ]
            )

        # Print combined table
        print(combined_table)

    def print_table(self):
        print(f'\n{"-"*60}\n\t  Details of process: {self.name}\n{"-"*60}\n')
        table = [[k, v] for k, v in self.to_dict().items()]
        print(tabulate(table, headers=["Attribute", "Value"], tablefmt="fancy_grid"))

    def add_transfer_coefficient(
        self, flow_input, flow_output, transfer_coefficient, uncertainty
    ):
        """
        Adds a transfer coefficient to the process.

        Args:
            input (str): The input flow.
            output (str): The output flow.
            transfer_coefficient (float): The transfer coefficient.
            uncertainty (float): The uncertainty of the transfer coefficient.
        """
        self.transfer_coefficients[flow_output] = {
            "input": flow_input,
            "output": flow_output,
            "transfer_coefficient": transfer_coefficient,
            "uncertainty": uncertainty,
        }

    def add_to_model(self, model):
        model.add_process(self)

    def add_input(self, flow):
        """
        Adds an input flow to the process.

        Args:
            flow (Flow): The input flow to add.
        """
        self.inputs[flow.name] = flow

    def add_output(self, flow):
        """
        Adds an output flow to the process.

        Args:
            flow (Flow): The output flow to add.
        """
        self.outputs[flow.name] = flow

    def remove_input(self, flow):
        """
        Removes an input flow from the process.

        Args:
            flow (Flow): The input flow to remove.
        """
        self.inputs.pop(flow)

    def remove_output(self, flow):
        """
        Removes an output flow from the process.

        Args:
            flow (Flow): The output flow to remove.
        """
        self.outputs.pop(flow)

    def clear_inputs(self):
        """
        Clears all input flows from the process.
        """
        self.inputs = {}

    def clear_outputs(self):
        """
        Clears all output flows from the process.
        """
        self.outputs = {}

    def get_total_input_flow(self):
        """
        Calculates the total input flow to the process.

        Returns:
            The total input flow to the process.
        """
        total_input_flow = sum(flow.amount for flow in self.inputs.values())
        return total_input_flow

    def get_total_output_flow(self):
        """
        Calculates the total output flow from the process.

        Returns:
            The total output flow from the process.
        """
        total_output_flow = sum(flow.amount for flow in self.outputs.values())
        return total_output_flow

    def add_transform_flow(self, flow, function):
        """
        Transforms an input flow and adds the resulting output flow to the process.

        Args:
            flow (Flow): The input flow to transform.
            function (function): The function to use for the transformation.
        """
        self.add_input(flow)
        out = flow.copy()
        out = function(flow)
        self.add_output(out)

    def has_input(self, flow):
        """
        Checks if an input flow is associated with the process.

        Args:
            flow (Flow): The input flow to check.

        Returns:
            True if the input flow is associated with the process, False otherwise.
        """
        return flow in self.inputs

    def has_output(self, flow):
        """
        Checks if an output flow is associated with the process.

        Args:
            flow (Flow): The output flow to check.

        Returns:
            True if the output flow is associated with the process, False otherwise.
        """
        return flow in self.outputs

    def has_tag(self, tag):
        """
        Checks if a tag is associated with the process.

        Args:
            tag (str): The tag to check.

        Returns:
            True if the tag is associated with the process, False otherwise.
        """
        return tag in self.tags

    def add_parameter(self, parameter):
        """
        Adds a parameter to the process.

        Args:
            parameter: The parameter to add.
        """
        self.parameters[parameter.name] = parameter

    def remove_parameter(self, parameter):
        """
        Removes a parameter from the process.

        Args:
            parameter: The parameter to remove.
        """
        self.parameters.pop(parameter)

    def to_dict(self):
        """
        Converts the process to a dictionary.

        Returns:
            A dictionary representation of the process.
        """
        return {
            "name": self.name,
            "description": self.description,
            "WS": self.WS,
            "transformation_level": self.transformation_level,
            "tags": self.tags,
            "inputs": [f"{x.name}:{x.amount}{x.unit}" for x in self.inputs.values()],
            "outputs": [f"{x.name}:{x.amount}{x.unit}" for x in self.outputs.values()],
            "parameters": self.parameters,
            "consumption_energy": self.consumption_energy,
            "consumption_water": self.consumption_water,
            "cost_operation": self.cost_operation,
            "cost_capital": self.cost_capital,
            "transfer_coefficients": [
                f'{x["input"]}--{x["transfer_coefficient"]}-->{x["output"]}'
                for x in self.transfer_coefficients.values()
            ],
        }

    def make_flowchart(self):
        """
        Creates an isolated process flow diagram for 
        the process, showing only the direct inputs and outputs.
        This is only reversing the syntax really, 
        it uses the function from the visualisation module.
        """
        make_flowchart(self)

    def output_table(self):
        """
        Creates a table of the output flows of the process.

        Returns:
            A table of the output flows of the process.
        """
        print(f"Inputs to process {self.name}")
        table = [
            [
                flow.name,
                flow.process_from,
                flow.process_to,
                flow.composition,
                flow.amount,
                flow.unit,
                flow.tags,
            ]
            for flow in self.inputs.values()
        ]
        print(
            tabulate(
                table,
                tablefmt="fancy_grid",
                headers=["Name", "From", "To", "Composition", "Amount", "Unit", "Tags"],
            )
        )

    def input_table(self):
        """
        Creates a table of the input flows of the process.

        Returns:
            A table of the input flows of the process.
        """
        print(f"\nOutputs from process {self.name}")
        table = [
            [
                flow.name,
                flow.process_from,
                flow.process_to,
                flow.composition,
                flow.amount,
                flow.unit,
                flow.tags,
            ]
            for flow in self.outputs.values()
        ]
        print(
            tabulate(
                table,
                tablefmt="fancy_grid",
                headers=["Name", "From", "To", "Composition", "Amount", "Unit", "Tags"],
            )
        )
