#%%

# Import the classes
from futuram import *
# import utility functions
# from utils.import_matter import import_matter_xlsx

#%%

dir_data = '../data/'


# Create the model
model = Model('test_system_ELV')

#%%  Add processes

process_xlsx = dir_data + 'ELV_ICE_processes.xlsx'
import_processes_xlsx(process_xlsx, model)

# the above function returns a dictionary of the processes
# process_data = import_processes_xlsx(process_xlsx, model)

# check they are there
print('\nThe processes in the model are:')
list(model.processes)
# %% Import transfer coefficients

transfercoefficients_xlsx = dir_data + 'ELV_ICE_TCs.xlsx'
import_transfercoefficients_xlsx(transfercoefficients_xlsx, model)

# check they are there for one process
smelter_cc = model.processes['smelter_cc']
list(smelter_cc.transfer_coefficients)

# %% Import flows

flows_xlsx = dir_data + 'ELV_ICE_flows.xlsx'
import_flows_xlsx(flows_xlsx, model)

# check that they are there
print('\nThe flows in the model are:')
list(smelter_cc.inputs)[0].to_dict()
list(smelter_cc.outputs)[0].to_dict()

model.add_flow(smelter_cc.inputs[0])
# model.list_flows()

for process in model.processes.values():
    print(process.name)
    for flow in process.inputs:
        print(flow.to_dict())
        model.add_flow(flow)
    for flow in process.outputs:
        model.add_flow(flow)
        print(flow.to_dict())

flow.add_to_model(model)
model.list_flows()

# %% Import matter
dir_comp = dir_data + 'ELV_ICE_compositions-split/'
import_matter.import_matter_bulk(dir_data, model)

model.products
# %% make a process flow diagram

model.flows
