""" model.py

This file contains the Model class, which is the \
    main class of the FutuRuM package.

The Model class contains all of the other classes, \
    and is the main object that is used to build a model.

"""
import random
# import json
import pandas as pd
from prettytable import PrettyTable
from tabulate import tabulate

from ..visualisation import make_flowchart, make_network
from ..utils.solve_flows import calculate_output_flows
from ..utils.object_import_export import export_object


class Model:
    """
    The Model class is the main class of the FutuRuM package.

    The Model class contains all of the other classes,\
          and is the main object that is used to build a model.

    Attributes:
        name (str): The name of the model.
        type (str): The type of the model. This is always 'model'.

        parameters (dict): A dictionary of the parameters in the model.
        scenarios (dict): A dictionary of the scenarios in the model.

        processes (dict): A dictionary of the processes in the model.
        flows (dict): A dictionary of the flows in the model.

        elements (dict): A dictionary of the elements in the model.
        compounds (dict): A dictionary of the compounds in the model.
        materials (dict): A dictionary of the materials in the model.
        components (dict): A dictionary of the components in the model.
        products (dict): A dictionary of the products in the model.
        matter (dict): A dictionary of all matter in the model.

        inputs (dict): A dictionary of the inputs to the model.
        outputs (dict): A dictionary of the outputs from the model.

        transfer_coefficients (dict): A dictionary of the transfer coefficients in the model.

    Dependencies:
        - pandas
        - json
        - prettytable
        - random

    """

    def __init__(self, name):
        self.name = name
        self.type = "model"
        self.parameters = {}
        self.scenarios = {}
        self.processes = {}
        self.flows = self.get_flows()
        self.elements = {}
        self.compounds = {}
        self.materials = {}
        self.components = {}
        self.products = {}
        self.matter = self.get_matter()
        self.inputs = self.get_inputs()
        self.outputs = self.get_outputs()
        self.transfer_coefficients = self.get_transfer_coefficients()

        print(f"\n{'=' * 50}\n\tCreated model: {self.name}\n{'=' * 50}\n")

    def export_model(self):
        """
        Exports the model as a json or pickle file

        """

        export_object(self)

    def calculate_flows(self):
        '''
        calculates the flows amounts iteratively in the model
        using the transfer coefficients, the composition of the flows
        and the input flows to the model

        '''
        calculate_output_flows(self, self)

    def make_flowchart_model(self):
        """
        Create a flowchart for the whole model, showing all processes and their inputs and outputs

        """
        make_flowchart(self)

    def make_network(self):
        """
        Create a network of the processes in the model.
        Uses the networkx package to make a directed graph of the processes and flows in the model.

        """
        make_network(self)

    def make_flowchart_processes(self):
        """
        Create isolated flowcharts for each process in the model,\
              showing only the process and its direct inputs and outputs

        """
        print(
            f'\n{"="*80}\n Making isolated flow charts for the\
{len(self.processes.values())} processes in model \'{self.name}\'\n{"="*80}\n'
        )
        for count, proc in enumerate(self.processes.values()):
            print(f"{count+1}/{len(self.processes.values())}.")
            proc.make_flowchart()

        print(f'{"="*80}\n Created {len(self.processes.values())} isolated process flowcharts \n {"="*80} \n')

    def get_transfer_coefficients(self):
        """
        Returns a dictionary of all transfer coefficients in the model,\
              with keys in the format "ProcessName - TCName"

        """
        transfer_coefficients = {}
        for process in self.processes.values():
            tcs = process.transfer_coefficients
            # Update keys with process name
            tcs = {f"{process.name} - {k}": v for k, v in tcs.items()}
            transfer_coefficients.update(tcs)
        self.transfer_coefficients = transfer_coefficients
        return self.transfer_coefficients

    def print_transfer_coefficients(self):
        """
        Prints all of the transfer coefficients of the model in a nice table

        """
        self.get_transfer_coefficients()
        table = PrettyTable()
        table.title = f'There are {len(self.transfer_coefficients.values())} \
            transfer coefficients in model "{self.name}"'
        table.field_names = [" Input", "Output",
                             "Transfer coefficient", "Uncertainty"]
        for tc in self.transfer_coefficients.values():
            tc_value = f'{tc["transfer_coefficient"]:.2f}'
            table.add_row([tc["output"], tc["input"],
                          tc_value, tc["uncertainty"]])

        table.align = "l"
        print(table)

    def print_flows_by_process(self):
        print(
            f'\n{"="*60}\n\t  There are {len(self.processes.values())}\
                  flows in model {self.name}\n{"="*60}\n'
        )
        for count, process in enumerate(self.processes.values()):
            print(
                f'\n{"-"*60}\n\t {count+1}/{len(self.processes.values())}.\
                      Flows of process: {process.name}\n{"-"*60}\n'
            )

            print(f"Inputs to process {process.name}")
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
                for flow in process.inputs.values()
            ]
            print(
                tabulate(
                    table,
                    tablefmt="fancy_grid",
                    headers=[
                        "Name",
                        "From",
                        "To",
                        "Composition",
                        "Amount",
                        "Unit",
                        "Tags",
                    ],
                )
            )

            print(f"\nOutputs from process {process.name}")
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
                for flow in process.outputs.values()
            ]
            print(
                tabulate(
                    table,
                    tablefmt="fancy_grid",
                    headers=[
                        "Name",
                        "From",
                        "To",
                        "Composition",
                        "Amount",
                        "Unit",
                        "Tags",
                    ],
                )
            )

    def print_matter(self):
        """
        prints the matter objects in the model

        """
        print(
            f'\n{"-"*60}\n\t There are {len(self.list_matter())} \
                matter objects in the model: {self.name}\n{"-"*60}\n '
        )
        print(*self.list_matter(), sep="\n")

    def print_matter_subclasses(self):
        """
        prints the matter subclasses in the model
        """
        table = PrettyTable()
        table.title = (
            f'There are {len(self.matter)} matter objects in model "{self.name}"'
        )
        table.field_names = [
            "Category",
            "Component",
            "Component composition (name, mass fraction))",
        ]

        for category in [
            "Products",
            "Components",
            "Materials",
            "Compounds",
            "Elements",
        ]:
            components = getattr(self, category.lower())
            for component in components:
                if category not in ["Elements", "Compounds"]:
                    component_composition = [
                        (k, v["mass_fraction"])
                        for k, v in list(components[component].composition.items())
                    ]
                    component_composition = ", ".join(
                        [f"{k}: {v}" for k, v in component_composition]
                    )
                else:
                    component_composition = "N/A"
                table.add_row([category, component, component_composition])
        table.align = "l"
        print(table)

    def get_flows(self):
        flows = {}
        for process in self.processes.values():
            flows.update(process.inputs)
            flows.update(process.outputs)

        self.flows = flows
        return self.flows

    def get_inputs(self):
        inputs = {}
        for process in self.processes.values():
            if not process.inputs.values():
                inputs[process.name] = {}
                for flow in process.outputs.values():
                    inputs[process.name][flow.composition] = flow.amount
        self.inputs = inputs
        return self.inputs

    def get_outputs(self):
        outputs = {}
        for process in self.processes.values():
            if not process.outputs.values():
                outputs[process.name] = {}
                for flow in process.inputs.values():
                    outputs[process.name][flow.composition] = flow.amount
        self.outputs = outputs
        return self.outputs

    def random_process(self):
        """
        Get a random process from the model.

        Returns:
            Process: The random process.

        """
        random_process = random.choice(list(self.processes.values()))

        return random_process

    def random_flow(self):
        """
        Get a random flow from the model.

        Returns:
            Flow: The random flow.
        """
        random_process = self.random_process()

        flows = random_process.inputs + random_process.outputs
        random_flow = random.choice(flows)

        return random_flow

    def random_matter(self):
        """
        Get a random matter object from the model.

        Returns:
            Element, Compound, Material, Component \
                or Product: The random matter object.

        """
        random_matter = random.choice(list(self.matter.values()))

        return random_matter

    def add_parameter(self, parameter):
        if type(parameter).__name__ == "Parameter":
            self.parameters[parameter.name] = parameter
        else:
            raise TypeError(
                "Only objects of type Parameter can be added to parameters."
            )

    def add_scenario(self, scenario):
        if type(scenario).__name__ == "Scenario":
            self.scenarios[scenario.name] = scenario
        else:
            raise TypeError(
                "Only objects of type Scenario can be added to scenarios.")

    def add_process(self, process):
        if type(process).__name__ == "Process":
            self.processes[process.name] = process
        else:
            raise TypeError(
                "Only objects of type Process can be added to processes.")

    def add_flow(self, flow):
        if type(flow).__name__ == "Flow":
            self.flows[flow.name] = flow
        else:
            raise TypeError("Only objects of type Flow can be added to flows.")

    def add_matter(self, matter):
        if type(matter).__name__ == "Element":
            self.elements[matter.name] = matter
        elif type(matter).__name__ == "Compound":
            self.compounds[matter.name] = matter
        elif type(matter).__name__ == "Material":
            self.materials[matter.name] = matter
        elif type(matter).__name__ == "Component":
            self.components[matter.name] = matter
        elif type(matter).__name__ == "Product":
            self.products[matter.name] = matter
        else:
            raise TypeError(
                "Only objects of type Element, Compound, Material, Component or Product can be added to matter."
            )

    def add_element(self, element):
        if type(element).__name__ == "Element":
            self.elements[element.name] = element
        else:
            raise TypeError(
                "Only objects of type Element can be added to elements.")

    def add_compound(self, compound):
        if type(compound).__name__ == "Compound":
            self.compounds[compound.name] = compound
        else:
            raise TypeError(
                "Only objects of type Compound can be added to compounds.")

    def add_material(self, material):
        if type(material).__name__ == "Material":
            self.materials[material.name] = material
        else:
            raise TypeError(
                "Only objects of type Material can be added to materials.")

    def add_component(self, component):
        if type(component).__name__ == "Component":
            self.components[component.name] = component
        else:
            raise TypeError(
                "Only objects of type Component can be added to components."
            )

    def add_product(self, product):
        if type(product).__name__ == "Product":
            self.products[product.name] = product
        else:
            raise TypeError(
                "Only objects of type Product can be added to products.")

    def get_parameter(self, parameter_name):
        return self.parameters.get(parameter_name)

    def get_scenario(self, scenario_name):
        return self.scenarios.get(scenario_name)

    def get_process(self, process_name):
        return self.processes.get(process_name)

    def get_flow(self, flow_name):
        return self.flows.get(flow_name)

    def get_element(self, element_name):
        return self.elements.get(element_name)

    def get_compound(self, compound_name):
        return self.compounds.get(compound_name)

    def get_material(self, material_name):
        return self.materials.get(material_name)

    def get_component(self, component_name):
        return self.components.get(component_name)

    def get_product(self, product_name):
        return self.products.get(product_name)

    def list_parameters(self):
        parameter_names = list(self.parameters.keys())
        parameter_names.sort()
        print(parameter_names, sep="\n")

    def list_scenarios(self):
        scenario_names = list(self.scenarios.keys())
        scenario_names.sort()
        print(scenario_names, sep="\n")

    def print_processes(self):
        table = PrettyTable()
        table.title = f'Processes in "{self.name}"'

        for process in self.processes.values():
            process_dict = process.to_dict()
            for key, value in process_dict.items():
                if isinstance(value, dict):
                    process_dict[key] = f"dict {len(value)}"
                elif isinstance(value, list):
                    process_dict[key] = f"list {len(value)}"
            table.add_row(process.to_dict().values())

        table.field_names = process.to_dict().keys()
        table.align = "l"
        print(table)

    def print_flows(self):
        table = PrettyTable()
        table.title = f'Flows in "{self.name}"'
        self.get_flows()
        for flow in self.flows.values():
            flow_dict = flow.to_dict()
            for key, value in flow_dict.items():
                if isinstance(value, dict):
                    flow_dict[key] = f"dict {len(value)}"
                elif isinstance(value, list):
                    flow_dict[key] = f"list {len(value)}"
            table.add_row(flow_dict.values())

        table.field_names = flow.to_dict().keys()
        table.align = "l"
        print(table)

    def list_elements(self):
        element_names = list(self.elements.keys())
        element_names.sort()
        print(element_names, sep="\n")

    def list_compounds(self):
        compound_names = list(self.compounds.keys())
        compound_names.sort()
        print(compound_names, sep="\n")

    def list_materials(self):
        material_names = list(self.materials.keys())
        material_names.sort()
        print(material_names, sep="\n")

    def list_components(self):
        component_names = list(self.components.keys())
        component_names.sort()
        print(component_names, sep="\n")

    def list_products(self):
        product_names = list(self.products.keys())
        product_names.sort()
        print(product_names)

    def get_matter(self):
        """
        makes a dictionary of all matter in the model from the \
            elements, compounds, materials, components and products

        """
        matter = {
            **self.elements,
            **self.compounds,
            **self.materials,
            **self.components,
            **self.products,
        }
        self.matter = matter
        return self.matter

    def list_matter(self):
        """ 

        """
        self.get_matter()
        matter_names = list(self.matter.keys())
        matter_names.sort()

        # for m in [self.elements, self.compounds, self.materials, self.components, self.products]:
        #     for matter_name, matter in m.items():
        #         print(matter_name)
        #         print(matter)
        #         print()
        return matter_names

#! the export functions need testing and improvement
    def to_dataframe(self):
        """
        Convert the model objects to a dataframe.

        Returns:
            pd.DataFrame: A dataframe representing the model objects.

        """
        data = []

        for model_object in [
            self.name,
            self.type,
            self.parameters,
            self.scenarios,
            self.processes,
            self.flows,
            self.elements,
            self.compounds,
            self.materials,
            self.components,
            self.products,
            self.matter,
            self.inputs,
            self.outputs,
            self.transfer_coefficients,
        ]:

            if isinstance(model_object, dict):
                for key, value in model_object.items():
                    data.append([key, value])
            else:
                data.append([model_object])

        df = pd.DataFrame(data)
        return df

    def to_excel(self, filename):
        """
        Write the model objects to an Excel file.

        Args:
            filename (str): The name of the Excel file.

        """
        df = self.to_dataframe()
        df.to_excel(filename, index=False)

    def to_csv(self, filename):
        """
        Write the model objects to a CSV file.

        Args:
            filename (str): The name of the CSV file.

        """
        df = self.to_dataframe()
        df.to_csv(filename, index=False)

    def to_json(self, filename):
        """
        Write the model objects to a JSON file.

        Args:
            filename (str): The name of the JSON file.

        """
        df = self.to_dataframe()
        df.to_json(filename, orient="records")

    def to_dict(self):
        """
        Convert the model objects to a dictionary.

        Returns:
            dict: A dictionary representing the model objects.

        """
        model_dict = {
            "name": self.name,
            "type": self.type,
            "parameters": self.parameters,
            "scenarios": self.scenarios,
            "processes": self.processes,
            "flows": self.flows,
            "elements": self.elements,
            "compounds": self.compounds,
            "materials": self.materials,
            "components": self.components,
            "products": self.products,
            "matter": self.matter,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "transfer_coefficients": self.transfer_coefficients,
        }

        return model_dict

    def list_parameter_attributes(self):
        print("Parameters:")
        for parameter_name, parameter in self.parameters.items():
            print(f"{parameter_name}: {parameter.value} {parameter.unit}")
            print(f"Description: {parameter.description}")
            print(f"Uncertainty: {parameter.uncertainty}")
            print(f"Data Sources: {', '.join(parameter.data_sources)}")
            print()

    def list_scenario_attributes(self):
        print("Scenarios:")
        for scenario_name, scenario in self.scenarios.items():
            print(f"{scenario_name}:")
            for parameter_name, value in scenario.parameters.items():
                print(f"{parameter_name}: {value}")
            print()
