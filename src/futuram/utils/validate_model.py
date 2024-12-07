"""
validate_model.py

This module contains functions for validating the model object.

Functions:
- validate_model(model):  Wrapper function that calls the other validation functions.
- validate_flows(model): Validates the flows in the model object to ensure that the \
    matter in the flow's composition and the to and from processes are in the model.
- validate_matter(model): Validates the matter referred to in the flow objects composition\
      to ensure that the matter is in the model.

Dependencies:
- ../classes/model.py
- ../classes/processes.py
- ../classes/matter.py
- ../classes/flows.py

"""


def validate_model(model):
    """
    Validates the model object to ensure that all the matter and processes \
        referred to in the model are in the model

    Parameters
    ----------
    model : Model

    Returns
    -------
    validity : bool
        True if the model is valid, False if not

    """
    # Validate the model
    print(f'\n\n{"="*90}\n\t Validating model: "{model.name}"\n{"="*90}')
    exceptions_flows = validate_flows(model)
    exceptions_matter = validate_matter(model)

    # If there are no exceptions, the model is valid
    if exceptions_flows == 0 and exceptions_matter == 0:
        print(
            f'\n\n{"="*60}\n\t** Model validated! **\n{"-"*90}\n All processes and matter referred to in the model are in the model: "{model.name}" \n{"="*60}\n'
        )
        validity = True
    else:
        print(
            f'\n{"="*90}\n\t ** Model validation failed! **\n {"-"*90}\n {exceptions_flows} flows and {exceptions_matter} matter objects referred to are not in the model: "{model.name}" \n check input data and try again \n{"="*90}\n'
        )
        validity = False

    # Return the validity, which is a boolean, can be used to control the flow of the program
    return validity


def validate_flows(model):
    """
    Validates the flows in the model object to ensure that the\
          matter in the flow's composition and the to and from processes are in the model

    Parameters
    ----------
    model : Model

    Returns
    -------
    exception_count : int
        The number of exceptions found

    """
    print(f'\n{"-"*60}\n\t Validating flows in model: "{model.name}"\n{"-"*60}')
    exception_count = []

    # Get the flows and processes in the model, then check that the processes \
    # referred to in the flows are in the model, if not, add them to the exception count
    for process_object in model.processes.values():
        for flow_process in process_object.inputs.values():
            try:
                model.processes[flow_process.process_to]
            except KeyError:
                exception_count.append(flow_process.process_to)
        for flow_process in process_object.outputs.values():
            try:
                model.processes[flow_process.process_from]
            except KeyError:
                exception_count.append(flow_process.process_from)

    # Remove duplicates from the exception count
    exception_count = sorted(list(set(exception_count)))

    # If there are no exceptions, the model is valid
    if len(exception_count) == 0:
        print(
            f'\n\t** Model flows validated **\n All processes referred to in flows are in the model: "{model.name}"'
        )
    else:
        print(
            f'\n\t** Model flows validation failed! **\n {len(exception_count)} processes referred to in flows are not in the model: "{model.name}",\n check input data and try again"'
        )
        for exception in exception_count:
            print("\t" + exception)

    # Return the number of exceptions
    return len(exception_count)


def validate_matter(model):
    """
    Validates the matter referred to in the flow objects\
          composition to ensure that the matter is in the model

    Parameters
    ----------
    model : Model

    Returns
    -------
    exception_count : int
        The number of exceptions found

    """
    print(f'\n{"-"*60}\n\t Validating matter in model: "{model.name}"\n{"-"*60}')
    model.get_matter()
    exception_count = []

    # Get the matter in the model, then check that the matter referred to in the flows \
    # are in the model, if not, add them to the exception count

    for process_object in model.processes.values():
        for flow_process in process_object.inputs.values():
            try:
                model.matter[flow_process.composition]
            except KeyError:
                exception_count.append(flow_process.composition)
        for flow_process in process_object.outputs.values():
            try:
                model.matter[flow_process.composition]
            except KeyError:
                exception_count.append(flow_process.composition)

    # Remove duplicates from the exception count
    exception_count = sorted(list(set(exception_count)))

    # If there are no exceptions, the model is valid
    if len(exception_count) == 0:
        print(
            f'\n\t** Model matter validated! **\n All matter referred to in flows are in the model: "{model.name}"'
        )
    else:
        print(
            f'\n\t** Model matter validation failed! **\n {len(exception_count)} matter objects referred to in flows are not in the model: "{model.name}",\n check input data and try again"'
        )
        for exception in exception_count:
            print("\t" + exception)

    # Return the number of exceptions
    return len(exception_count)
