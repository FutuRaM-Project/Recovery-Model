

def validate_model(model):
    """
    Validates the model object to ensure that all the matter and processes referred to in the model are in the model
    """
    print(f'\n\n{"="*90}\n\t Validating model: "{model.name}"\n{"="*90}')
    exceptions_flows = validate_flows(model)
    exceptions_matter = validate_matter(model)

    if exceptions_flows == 0 and exceptions_matter == 0:
        print(f'\n\n{"="*60}\n\t** Model validated! **\n{"-"*90}\n  All processes and matter referred to in the model are in the model: "{model.name}" \n{"="*60}\n')
    else:
        print(f'\n{"="*90}\n\t ** Model validation failed! **\n {"-"*90}\n {exceptions_flows} flows and {exceptions_matter} matter objects referred to are not in the model: "{model.name}" \n check input data and try again \n{"="*90}\n')


def validate_flows(model):
    """
    Validates the flows in the model object to ensure that the matter in the flow's composition and the to and from processes are in the model
    """
    print(f'\n{"-"*60}\n\t Validating flows in model: "{model.name}"\n{"-"*60}')
    exception_count = []
    for process, process_object in model.processes.items():
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
    
    exception_count = sorted(list(set(exception_count)))

    if len(exception_count) == 0:
        print(f'\n\t** Model flows validated **\n All processes referred to in flows are in the model: "{model.name}"')
    else:
        print(f'\n\t** Model flows validation failed! **\n {len(exception_count)} processes referred to in flows are not in the model: "{model.name}",\n check input data and try again"')
        for exception in exception_count:
            print('\t' + exception)
    
    
    return len(exception_count)
    
def validate_matter(model):
    """
    Validates the matter referred to in the flow objects composition to ensure that the matter is in the model
    """
    print(f'\n{"-"*60}\n\t Validating matter in model: "{model.name}"\n{"-"*60}')
    model.get_matter()
    exception_count = []
    for process, process_object in model.processes.items():
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

    exception_count = sorted(list(set(exception_count)))
    
    if len(exception_count) == 0:
        print(f'\n\t** Model matter validated! **\n All matter referred to in flows are in the model: "{model.name}"')
    else:
        print(f'\n\t** Model matter validation failed! **\n {len(exception_count)} matter objects referred to in flows are not in the model: "{model.name}",\n check input data and try again"')
        for exception in exception_count:
            print("\t"+exception)
    
    return len(exception_count)