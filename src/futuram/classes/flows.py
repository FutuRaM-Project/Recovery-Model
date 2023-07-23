import json
import pandas as pd

from .processes import Process

class Flow:
    """
    A class representing a flow of material or energy between two points.

    Attributes:
        name (str): The name of the flow.
        parameters (dict): A dictionary of parameters associated with the flow.
        tags (list): A list of tags associated with the flow.
        to (str): The destination of the flow.
        from_ (str): The source of the flow.
        amount (float): The amount of material or energy in the flow.
        composition (dict): A dictionary representing the composition of the flow.
        unit (str): The unit of measurement for the flow.
    """
    def __init__(self, model, process_from, process_to, composition):
        self.name = process_from + "_to_" + process_to
        self.parameters = {}
        self.tags = []
        self.process_from = process_from
        self.process_to = process_to
        self.amount = None
        self.composition = composition
        self.unit = None
        # self.add_composition_to_model(model)

##! THIS NEXT TWO FUNCTIONS SHOLD SET THE TO AND FROM PROCESSES TO BE THE OBJECTS IN THE MODEL, NOT JUST THE NAMES, ALSO ADD THE FLOW TO THE INPUTS AND OUTPUTS OF THE PROCESSES IF NOT PRESENT. but it is not working for some reason
    def set_to(self, model, process_to):
        """
        Sets the destination of the flow to a process object if in the model
        Adds the process if not in the model

        Args:
            to (str): The destination of the flow.
        """
        try :
            process = model.processes[process_to]
            self.process_to = process
            if self not in process.inputs:
                process.add_input(self)
                print(f"Flow: {self.name} added to process: {process.name}")
            else:
                print(f"Flow {self.name} already in process: {process.name}")

        except KeyError:
            print(f"Process: {process_to} not found in model, adding to model")
            process = Process(process_to)
            process.add_input(self)
            model.add_process(process)
            print(f"Flow: {self.name} added to process: {process.name}")

        _process_to = process
        return _process_to

    def set_from(self, model, process_from):
        """
        Sets the source of the flow to a process object if in the model
        Adds the process if not in the model

        Args:
            from_ (str): The source of the flow.
        """
        try :
            process = model.processes[process_from]
            self.process_from = process
            if self not in process.outputs:
                process.add_output(self)
                print(f"Flow: {self.name} added to process: {process.name}")
            else:
                print(f"Flow {self.name} already in process: {process.name}")

        except KeyError:
            print(f"Process: {process_from} not found in model, adding to model")
            process = Process(process_from)
            process.add_output(self)
            model.add_process(process)
            print(f"Flow: {self.name} added to process: {process.name}")
        _process_from = process
        return _process_from

    def add_composition_to_model(self, model):
        """
        Adds the composition of the flow to the model's matter dictionary if not present.

        Args:
            model (Model): The model object to add the composition to.
        """
        for matter_name in self.composition:
            try:
                if matter_name not in model.matter:
                    model.matter[matter_name] = Matter(matter_name, self.composition[matter_name])
            except Exception as e:
                print(e)

    #TODO: Add a method to check if the composition consists of valid matter
    def set_composition(self, composition):
        """
        Sets the composition of the flow.

        Args:
            composition (dict): A dictionary representing the composition of the flow.

        Raises:
            TypeError: If the composition is not a dictionary or if the keys are not strings or the values are not numbers.
            ValueError: If the sum of the composition values is not equal to 1.
        """
        if not isinstance(composition, dict):
            raise TypeError("Composition must be a dictionary.")
        if not all(isinstance(key, str) for key in composition.keys()):
            raise TypeError("Composition keys must be strings.")
        if not all(isinstance(value, (int, float)) for value in composition.values()):
            raise TypeError("Composition values must be numbers.")
        if sum(composition.values()) != 1:
            raise ValueError("Composition values must add up to 1.")
        self.composition = composition
        
    def set_amount(self, amount):
        """
        Sets the amount of material or energy in the flow.

        Args:
            amount (float): The amount of material or energy in the flow.

        Raises:
            TypeError: If the amount is not a number.
        """
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        self.amount = amount

    def add_to_model(self, model):
        model.add_flow(self)
    
    def set_parameter(self, parameter_name, value):
        """
        Sets a parameter associated with the flow.

        Args:
            parameter_name (str): The name of the parameter.
            value: The value of the parameter.
        """
        self.parameters[parameter_name] = value

    def get_parameter(self, parameter_name):
        """
        Gets the value of a parameter associated with the flow.

        Args:
            parameter_name (str): The name of the parameter.

        Returns:
            The value of the parameter, or None if the parameter does not exist.
        """
        return self.parameters.get(parameter_name)

    def has_parameter(self, parameter_name):
        """
        Checks if a parameter is associated with the flow.

        Args:
            parameter_name (str): The name of the parameter.

        Returns:
            True if the parameter is associated with the flow, False otherwise.
        """
        return parameter_name in self.parameters

    def remove_parameter(self, parameter_name):
        """
        Removes a parameter associated with the flow.

        Args:
            parameter_name (str): The name of the parameter.
        """
        if self.has_parameter(parameter_name):
            del self.parameters[parameter_name]

    def get_all_parameters(self):
        """
        Gets all parameters associated with the flow.

        Returns:
            A dictionary of all parameters associated with the flow.
        """
        return self.parameters

    def clear_parameters(self):
        """
        Clears all parameters associated with the flow.
        """
        self.parameters = {}

    def add_tag(self, tag):
        """
        Adds a tag to the flow.

        Args:
            tag (str): The tag to add.
        """
        self.tags.append(tag)

    def remove_tag(self, tag):
        """
        Removes a tag from the flow.

        Args:
            tag (str): The tag to remove.
        """
        if tag in self.tags:
            self.tags.remove(tag)

    def get_tags(self):
        """
        Gets all tags associated with the flow.

        Returns:
            A list of all tags associated with the flow.
        """
        return self.tags

    def set_to(self, process_to):
        """
        Sets the destination of the flow.

        Args:
            to (str): The destination of the flow.
        """
        self.process_to = process_to

    def set_from(self, process_from):
        """
        Sets the source of the flow.

        Args:
            from_ (str): The source of the flow.
        """
        self.process_from_ = process_from

    def get_to(self):
        """
        Gets the destination of the flow.

        Returns:
            The destination of the flow.
        """
        return self.process_to

    def get_from(self):
        """
        Gets the source of the flow.

        Returns:
            The source of the flow.
        """
        return self.process_from

    def to_dict(self):
        """
        Converts the flow to a dictionary.

        Returns:
            A dictionary representing the flow.
        """
        flow_dict = {
            'Name': self.name,
            'Tags': self.tags,
            'To': self.process_to,
            'From': self.process_from,
            'Amount': self.amount,
            'Unit': self.unit,
            'Composition': self.composition,
            'Parameters': self.parameters,

        }
        return flow_dict

    def to_series(self):
        """
        Converts the flow to a Pandas Series.

        Returns:
            A Pandas Series representing the flow.
        """
        flow_dict = self.to_dict()
        series = pd.Series(flow_dict)
        return series
    
    def add_to_model(self, model):
        """
        Adds the flow to a given model.

        Args:
            model (Model): The model to add the flow to.
        """
        model.add_flow(self)


    
    '''

    # Example usage:

    # Create flows
    flow_1 = Flow("Flow_1", "Process_1", "Process_2", 100, "kg")

    # Set composition
    flow_1.set_composition({"matter_1": 0.4, "matter_2": 0.6})
    
    # Set amount
    flow_1.set_amount(200)

    # Set parameter
    flow_1.set_parameter("Parameter_1", 1)

    # Add tag
    flow_1.add_tag("Tag_1")

    flow_1.to_dict()

# Output:
        # {'Name': 'Flow_1',
        #  'Tags': ['Tag_1'],
        #  'To': 'Process_1',
        #  'From': 'Process_2',
        #  'Amount': 200,
        #  'Unit': 'kg',
        #  'Composition': {'matter_1': 0.5, 'matter_2': 0.5},
        #  'Parameters': {'Parameter_1': 1}}

    '''
