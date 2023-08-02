"""
parameters.py 

This file contains the classes for parameters and scenarios.

The Parameter class represents a parameter, which can be either internal or external.

The Scenario class represents a scenario, which is a collection of parameters.

The EXTERNAL_PARAMETERS list contains the default external parameters.


"""

import json
import pandas as pd


# Define a class for parameters
class Parameter:
    """
    A class to represent a parameter.

    """

    def __init__(
        self,
        name,
        value=None,
        unit=None,
        description=None,
        data_sources=None,
        lower_bound=None,
        upper_bound=None,
        uncertainty=None,
        internal=True,
    ):

        self.name = name
        self.value = value
        self.unit = unit
        self.description = description
        self.data_sources = []
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.uncertainty = uncertainty
        self.internal = internal

    def __repr__(self):
        """
        Return a string representation of the parameter.

        Returns
        -------
        str
            The string representation of the parameter.
        """
        return f"{self.name}: {self.value} {self.unit}"

    def add_to_model(self, model):
        model.add_parameter(self)

    def set_description(self, description):
        """
        Set the description of the parameter.

        Parameters
        ----------
        description : str
            The description of the parameter.
        """
        self.description = description

    def add_data_source(self, source):
        """
        Add a data source to the parameter.

        Parameters
        ----------
        source : str
            The data source to add.
        """
        self.data_sources.append(source)

    def set_bounds(self, lower_bound, upper_bound):
        """
        Set the bounds of the parameter.

        Parameters
        ----------
        lower_bound : float
            The lower bound of the parameter.
        upper_bound : float
            The upper bound of the parameter.
        """
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def set_uncertainty(self, uncertainty):
        """
        Set the uncertainty of the parameter.

        Parameters
        ----------
        uncertainty : float
            The uncertainty of the parameter.
        """
        self.uncertainty = uncertainty

    def set_internal(self, internal):
        """
        Set the parameter as internal.

        Parameters
        ----------
        internal : bool
            Whether the parameter is internal or external.
        """
        self.internal = True

    def set_external(self):
        """
        Set the parameter as external.
        """
        self.internal = False

    def get_description(self):
        """
        Get the description of the parameter.

        Returns
        -------
        str
            The description of the parameter.
        """
        return self.description

    def get_data_sources(self):
        """
        Get the data sources of the parameter.

        Returns
        -------
        list
            The data sources of the parameter.
        """
        return self.data_sources

    def get_bounds(self):
        """
        Get the bounds of the parameter.

        Returns
        -------
        tuple
            The lower and upper bounds of the parameter.
        """
        return self.lower_bound, self.upper_bound

    def get_uncertainty(self):
        """
        Get the uncertainty of the parameter.

        Returns
        -------
        float
            The uncertainty of the parameter.
        """
        return self.uncertainty

    def is_internal(self):
        """
        Check if the parameter is internal.

        Returns
        -------
        bool
            Whether the parameter is internal or external.
        """
        return self.internal

    def to_dict(self):
        """
        Convert the parameter to a dictionary.

        Returns
        -------
        dict
            The dictionary representation of the parameter.
        """
        parameter_dict = {
            "Name": self.name,
            "Value": self.value,
            "Unit": self.unit,
            "Description": self.description,
            "Data Sources": self.data_sources,
            "Bounds": (self.lower_bound, self.upper_bound),
            "Uncertainty": self.uncertainty,
            "Internal": self.internal,
        }
        return parameter_dict

    def to_series(self):
        """
        Convert the parameter to a Pandas Series.

        Returns
        -------
        pandas.Series
            The Series representation of the parameter.
        """
        parameter_dict = self.to_dict()
        series = pd.Series(parameter_dict)
        return series


# Define a list of default external parameters (we could also read these from a file)
EXTERNAL_PARAMETERS = [
    Parameter("Parameter1", 1, "units"),
    Parameter("Parameter2", 2, "units"),
    Parameter("Parameter3", 3, "units"),
    Parameter("Parameter4", 4, "units"),
    Parameter("Parameter5", 5, "units"),
]

for parameter in EXTERNAL_PARAMETERS:
    parameter.set_external()


# Define a class for scenarios
class Scenario:
    """
    A class to represent a scenario.

    """

    def __init__(self, name):
        """

        """
        self.name = name
        self.description = None
        self.parameters = {param.name: param for param in EXTERNAL_PARAMETERS}

    def add_to_model(self, model):
        model.add_scenario(self)

    def set_parameter(self, parameter_name, value):
        """
        Set the value of a parameter in the scenario.

        Parameters
        ----------
        parameter_name : str
            The name of the parameter to set.
        value : float
            The value to set the parameter to.
        """
        self.parameters[parameter_name] = value
        if sum([param.value for param in self.parameters.values()]) != 1:
            raise ValueError("Parameter values must add up to 1.")

    def set_description(self, description):
        """
        Set the description of the scenario.

        Parameters
        ----------
        description : str
            The description of the scenario.
        """
        self.description = description

    def get_parameter(self, parameter_name):
        """
        Get the value of a parameter in the scenario.

        Parameters
        ----------
        parameter_name : str
            The name of the parameter to get.

        Returns
        -------
        float
            The value of the parameter.
        """
        return self.parameters.get(parameter_name)

    def has_parameter(self, parameter_name):
        """
        Check if a parameter exists in the scenario.

        Parameters
        ----------
        parameter_name : str
            The name of the parameter to check.

        Returns
        -------
        bool
            Whether the parameter exists in the scenario.
        """
        return parameter_name in self.parameters

    def remove_parameter(self, parameter_name):
        """
        Remove a parameter from the scenario.

        Parameters
        ----------
        parameter_name : str
            The name of the parameter to remove.
        """
        if self.has_parameter(parameter_name):
            del self.parameters[parameter_name]

    def get_all_parameters(self):
        """
        Get all parameters in the scenario.

        Returns
        -------
        dict
            The parameters in the scenario.
        """
        return self.parameters

    def clear_parameters(self):
        """
        Clear all parameters in the scenario.
        """
        self.parameters = {}

    def to_dict(self):
        """
        Convert the scenario to a dictionary.

        Returns
        -------
        dict
            The dictionary representation of the scenario.
        """
        scenario_dict = {
            "Name": self.name,
            "Description": self.description,
            "Parameters": self.parameters,
        }
        return scenario_dict

    def to_series(self):
        """
        Convert the scenario to a Pandas Series.

        Returns
        -------
        pandas.Series
            The Series representation of the scenario.
        """
        scenario_dict = self.to_dict()
        series = pd.Series(scenario_dict)
        return series


""" # Example usage:

# Create scenarios
scenario_bau = Scenario("Scenario_BAU")
scenario_rec = Scenario("Scenario_REC")
scenario_cir = Scenario("Scenario_CIR")

scenario_bau.set_description("Business as usual")
scenario_rec.set_description("Recovery")
scenario_cir.set_description("Circularity")


scenario_bau.to_dict()
 """
