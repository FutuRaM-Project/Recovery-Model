"""
solve_flows.py

This is a script to solve the flows in the model.

This is an iterative 'graph traversal' algorithm that 
loops over the processes in the model,

The first amounts for the output flows from the first processes
are calculated with the input flows to these, and the transfer coefficients.

Then, the amounts for the output flows from the next processes
are calculated with the input flows to these, and the transfer coefficients.

This is repeated until all flows have been calculated.

!# there is clearly still a bug or two in this script, but it's a start

"""
#%%

# loop over the outputs of a process and match the composition of the output flow the transfer coefficient
def calculate_output_flows(process):
    
    next_processes = []
    for flow_out in process.outputs.values():
        print(f'Flow in: {flow_out.name}')
        tc = process.transfer_coefficients[flow_out.composition]
        
        # loop over the inputs of the process
        for flow_in in process.inputs.values():
            
            # if the process is just a transfer (like collection), the composition of the output flow is the same as the input flow

            if flow_in.composition == flow_out.composition:
                flow_out.amount = flow_in.amount * tc['transfer_coefficient']
                print(f'Transfer flow calculated for: {flow_out.name} from {flow_in.name}')
            
            # if not, the composition of the output flow is one of the fractions in the input flow
            else:
                fractions = model.matter[flow_in.composition].composition
                
                try:
                    flow_out.amount = flow_out.amount + \
                                    fractions[flow_out.composition]['mass_fraction'] * \
                                        tc['transfer_coefficient']
                    
                    print(f'Match for {flow_out.composition} --> {flow_out.amount}')
                except KeyError:
                    print(f'\t ** No match for {flow_in.composition} with {flow_out.composition}')
        
        # if the process has outputs, add the next process to the list of next processes
        if flow_out.process_to not in next_processes and \
            model.processes[flow_out.process_to].outputs:
            next_processes.append(flow_out.process_to)

    return next_processes

#%%

def calculate_next_processes(next_processes):
    next_next_processes = []
    for process in next_processes:
        process = model.processes[process]
        next_next_processes += calculate_output_flows(process)
    
    return next_next_processes

next_next_processes = calculate_next_processes(next_processes)
#%%
# loop over all processes in the model
def calculate_model_flows(model):
    inputs = model.get_inputs()
    next_processes = []
    for process in inputs.keys():
        process = model.processes[process]
        next_processes += calculate_output_flows(process)
    
    next_next_processes = calculate_next_processes(next_processes)

    return next_next_processes

#%% For testing the script, you can use any model
# if the import isnt working just run the test model in and use same kernel
# to get the model variable to feed the calculate_model_flows function

#! not working now
# if __name__ == '__main__':
#     import subprocess
#     subprocess.run(['python', '../../src/examples/ELV/scripts/TestModel_ELV.py'])
#     model = example.model
#     calculate_model_flows(model)
#     model.get_flows()
#     model.print_flows()
#     model.make_flowchart_model()

# %% just run the test model in and use same kernel

calculate_model_flows(model)
model.get_flows()
model.print_flows()
model.make_flowchart_model()