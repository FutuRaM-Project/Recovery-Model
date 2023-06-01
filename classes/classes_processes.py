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
    def __init__(self, name, description="", tags=None):
        self.name = name
        self.description = description
        self.tags = tags if tags is not None else []
        self.WS = []
        self.inputs = []
        self.outputs = []
        self.parameters = []
    
    def add_input(self, flow):
        """
        Adds an input flow to the process.

        Args:
            flow (Flow): The input flow to add.
        """
        self.inputs.append(flow)
    
    def add_output(self, flow):
        """
        Adds an output flow to the process.

        Args:
            flow (Flow): The output flow to add.
        """
        self.outputs.append(flow)
    
    def remove_input(self, flow):
        """
        Removes an input flow from the process.

        Args:
            flow (Flow): The input flow to remove.
        """
        self.inputs.remove(flow)
    
    def remove_output(self, flow):
        """
        Removes an output flow from the process.

        Args:
            flow (Flow): The output flow to remove.
        """
        self.outputs.remove(flow)
    
    def clear_inputs(self):
        """
        Clears all input flows from the process.
        """
        self.inputs = []
    
    def clear_outputs(self):
        """
        Clears all output flows from the process.
        """
        self.outputs = []
    
    def get_total_input_flow(self):
        """
        Calculates the total input flow to the process.

        Returns:
            The total input flow to the process.
        """
        total_input_flow = sum(flow.amount for flow in self.inputs)
        return total_input_flow
    
    def get_total_output_flow(self):
        """
        Calculates the total output flow from the process.

        Returns:
            The total output flow from the process.
        """
        total_output_flow = sum(flow.amount for flow in self.outputs)
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
        self.add_output(flow)
    
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
        self.parameters.append(parameter)
    
    def remove_parameter(self, parameter):
        """
        Removes a parameter from the process.

        Args:
            parameter: The parameter to remove.
        """
        self.parameters.remove(parameter)

    def to_dict(self):
        """
        Converts the process to a dictionary.

        Returns:
            A dictionary representation of the process.
        """
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "WS": self.WS,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters
        }