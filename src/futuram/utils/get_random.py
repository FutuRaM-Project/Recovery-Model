"""
get_random.py

This file contains functions to get random objects from a model.

Functions:
- get_random_process(model): Get a random process from the model.
- get_random_flow(model): Get a random flow from the model.
- get_random_matter(model): Get a random matter object from the model.

Dependencies:
- random
- model.py
- processes.py
- matter.py
- flows.py

"""


from random import choice


def get_random_process(model):
    """
    Get a random process from the model.

    :param model: The model to get the process from.
    :return: The random process.

    """
    random_process = choice(list(model.processes.values()))

    return random_process


def get_random_flow(model):
    """
    Get a random flow from the model.

    :param model: The model to get the flow from.
    :return: The random flow.

    """
    random_process = get_random_process(model)

    flows = random_process.inputs + random_process.outputs
    random_flow = choice(flows)

    return random_flow


def get_random_matter(model):
    """
    Get a random matter object from the model.
    :param model: The model to get the matter object from.
    :return: The random matter object.
    
    """

    random_matter = choice(list(model.matter.values()))

    return random_matter
