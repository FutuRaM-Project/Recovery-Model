# from FutuRaM-ecoveryModel import visualisation.create_process_flow_diagram 
# import create_process_flow_diagram
# from utils.create_sankey_diagram import create_sankey_diagram
# from utils.create_process_tree_diagram import create_process_tree_diagram

import pandas as pd
import json

class Model:
    def __init__(self, name):
        self.name = name
        self.parameters = {}
        self.scenarios = {}
        self.processes = {}
        self.flows = {}
        self.elements = {}
        self.compounds = {}
        self.materials = {}
        self.components = {}
        self.products = {}

    def add_parameter(self, parameter):
        if type(parameter).__name__ == 'Parameter':
            self.parameters[parameter.name] = parameter
        else:
            raise TypeError("Only objects of type Parameter can be added to parameters.")

    def add_scenario(self, scenario):
        if type(scenario).__name__ == 'Scenario':
            self.scenarios[scenario.name] = scenario
        else:
            raise TypeError("Only objects of type Scenario can be added to scenarios.")

    def add_process(self, process):
        if type(process).__name__ == 'Process':
            self.processes[process.name] = process
        else:
            raise TypeError("Only objects of type Process can be added to processes.")

    def add_flow(self, flow):
        if type(flow).__name__ == 'Flow':
            self.flows[flow.name] = flow
        else:
            raise TypeError("Only objects of type Flow can be added to flows.")

    def add_element(self, element):
        if type(element).__name__ == 'Element':
            self.elements[element.name] = element
        else:
            raise TypeError("Only objects of type Element can be added to elements.")

    def add_compound(self, compound):
        if type(compound).__name__ == 'Compound':
            self.compounds[compound.name] = compound
        else:
            raise TypeError("Only objects of type Compound can be added to compounds.")

    def add_material(self, material):
        if type(material).__name__ == 'Material':
            self.materials[material.name] = material
        else:
            raise TypeError("Only objects of type Material can be added to materials.")

    def add_component(self, component):
        if type(component).__name__ == 'Component':
            self.components[component.name] = component
        else:
            raise TypeError("Only objects of type Component can be added to components.")

    def add_product(self, product):
        if type(product).__name__ == 'Product':
            self.products[product.name] = product
        else:
            raise TypeError("Only objects of type Product can be added to products.")

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
        print(parameter_names)

    def list_scenarios(self):
        scenario_names = list(self.scenarios.keys())
        scenario_names.sort()
        print(scenario_names)

    def list_processes(self):
        process_names = list(self.processes.keys())
        process_names.sort()
        print(process_names)

    def list_flows(self):
        flow_names = list(self.flows.keys())
        flow_names.sort()
        print(flow_names)

    def list_matters(self):
        matter_names = list(self.elements.keys()) + list(self.compounds.keys()) + list(self.materials.keys()) + list(self.components.keys()) + list(self.products.keys())
        matter_names.sort()
        print(matter_names)

    def list_elements(self):
        element_names = list(self.elements.keys())
        element_names.sort()
        print(element_names)

    def list_compounds(self):
        compound_names = list(self.compounds.keys())
        compound_names.sort()
        print(compound_names)

    def list_materials(self):
        material_names = list(self.materials.keys())
        material_names.sort()
        print(material_names)

    def list_components(self):
        component_names = list(self.components.keys())
        component_names.sort()
        print(component_names)

    def list_products(self):
        product_names = list(self.products.keys())
        product_names.sort()
        print(product_names)

    def to_dataframe(self):
        """
        Convert the model objects to a dataframe.

        Returns:
            pd.DataFrame: A dataframe representing the model objects.
        """
        data = []

        for objects in [self.parameters, self.scenarios, self.processes, self.flows, self.elements,
                        self.compounds, self.materials, self.components, self.products]:
            for obj_name, obj in objects.items():
                data.append(obj.to_dict())

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
        df.to_json(filename, orient='records')

    def to_dict(self):
        """
        Convert the model objects to a dictionary.

        Returns:
            dict: A dictionary representing the model objects.
        """
        data = {}

        for objects in [self.parameters, self.scenarios, self.processes, self.flows, self.elements,
                        self.compounds, self.materials, self.components, self.products]:
            for obj_name, obj in objects.items():
                data[obj_name] = obj.to_dict()

        return data

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

    def build_process_flow_diagram(self, subclass=None, filter_tags=None, filter_value=None, filename_suffix=''):
        filename = create_process_flow_diagram(self, filter_tags, filter_value, filename_suffix)

        # Modify the filename as desired
        # ...

        print(f"Process flow diagram saved as {filename}")

    # def build_sankey_diagram(self, subclass=None, filter_tags=None, filter_value=None, filename_suffix=''):
    #     filename = create_sankey_diagram(self, filter_tags, filter_value, filename_suffix)

    #     # Modify the filename as desired
    #     # ...

    #     print(f"Sankey diagram saved as {filename}")

    # def build_process_tree_diagram(self, subclass=None, filter_tags=None, filter_value=None, filename_suffix=''):
    #     filename = create_process_tree_diagram(self)

    #     # Modify the filename as desired
    #     # ...

    #     print(f"Process tree diagram saved as {filename}")


    