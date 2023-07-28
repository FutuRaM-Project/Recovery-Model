"""
flows.py

This module contains the Flow class.

Classes:
- Flow: A class representing a flow of material or energy between two points.

Dependencies:
- pandas
- matter.py
- processes.py
"""

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

    def __init__(self, model, process_from, process_to, composition, unit="kg"):
        self.name = process_from + "_to_" + process_to
        self.type = "flow"
        self.parameters = {}
        self.tags = []
        self.process_from = process_from
        self.process_to = process_to
        self.amount = 0
        self.composition = composition
        self.unit = unit
        self.model = model
        # self.add_composition_to_model(model)

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
        print(f"Flow: {self.name} amount set to: {self.amount} {self.unit}")

        for flow in self.model.processes[self.process_to].outputs.values():
            flow.calculate_amount(self.model)

    def calculate_amount(self, model):
        """
        Calculates the amount of material or energy in the flow.

        Args:
            model (Model): The model object to use for the calculation.
        """
        process = self.model.processes[self.process_from]
        fractions_out = [flow.to_dict() for flow in process.outputs.values()]

        fractions_in = [
            model.matter[flow.composition].composition
            for flow in process.inputs.values()
        ]

        for flow in process.inputs.values():
            amount = flow.amount
            flow_composition_in = model.matter[flow.composition].composition
            for fraction in flow_composition_in.values():
                fraction["amount"] = float(amount) * float(fraction["mass_fraction"])
            flow.fractions = flow_composition_in

        for flow_out in process.outputs.values():
            for flow_in in process.inputs.values():
                try:
                    flow_out.set_amount(
                        flow_in.fractions[flow_out.composition]["amount"]
                        * float(
                            process.transfer_coefficients[flow_out.composition][
                                "transfer_coefficient"
                            ]
                        )
                    )
                    print(flow_out.amount)
                except KeyError as error:
                    print(error)

    ##! THIS NEXT TWO FUNCTIONS SHOLD SET THE TO AND FROM PROCESSES TO BE THE OBJECTS IN THE MODEL,
    ##!  NOT JUST THE NAMES, ALSO ADD THE FLOW TO THE INPUTS AND OUTPUTS OF THE PROCESSES IF
    #!! NOT PRESENT. but it is not working for some reason
    def set_to(self, model, process_to):
        """
        Sets the destination of the flow to a process object if in the model
        Adds the process if not in the model

        Args:
            to (str): The destination of the flow.
        """
        try:
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
        try:
            process = model.processes[process_from]
            self.process_from = process
            if self not in process.outputs:
                self.validate_flow(self, model)
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

    def validate_flow(self, flow, model):
        """
        Checks if the flow is valid, i.e. if the composition and the
        linked processes are valid and in the model
        """
        if flow.composition not in model.matter:
            raise ValueError(
                f"Flow: {flow.name} composition: {flow.composition} not found in model"
            )
        else:
            print(f"Flow: {flow.name} composition: {flow.composition} found in model")

        if flow.process_from not in model.processes:
            raise ValueError(
                f"Flow: {flow.name} process_from: {flow.process_from} not found in model"
            )

        if flow.process_to not in model.processes:
            raise ValueError(
                f"Flow: {flow.name} process_to: {flow.process_to} not found in model"
            )

    # def add_composition_to_model(self, model):
    #     """
    #     Adds the composition of the flow to the model's matter dictionary if not present.

    #     Args:
    #         model (Model): The model object to add the composition to.
    #     """
    #         if self.composition not in model.matter:
    #             model.matter[matter_name] = Matter(matter_name, self.composition[matter_name])
    #         except Exception as e:
    #             print(e)

    # TODO: Add a method to check if the composition consists of valid matter
    def set_composition(self, composition):
        """
        Sets the composition of the flow.

        Args:
            composition (dict): A dictionary representing the composition of the flow.

        Raises:
            TypeError: If the composition is not a dictionary or if the keys
              are not strings or the values are not numbers.
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

    def add_to_model(self, model):
        """
        Adds the flow to a given model.
        """
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

    def to_dict(self):
        """
        Converts the flow to a dictionary.

        Returns:
            A dictionary representing the flow.
        """
        flow_dict = {
            "Name": self.name,
            "Tags": self.tags,
            "To": self.process_to,
            "From": self.process_from,
            "Amount": self.amount,
            "Unit": self.unit,
            "Composition": self.composition,
            "Parameters": self.parameters,
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
