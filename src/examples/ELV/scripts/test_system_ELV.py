#%%
import futuram as f


#%% Take the composition data and split it into individual csvs for each matter

dir_data = '../data/'

# Create the model
model = f.Model('test_system_ELV')

#%%  Add processes

process_xlsx = dir_data + 'ELV_ICE_processes.xlsx'
f.utils.import_processes_xlsx(process_xlsx, model)

# the above function returns a dictionary of the processes
# process_data = import_processes_xlsx(process_xlsx, model)

# check they are there
print('\nThe processes in the model are:')
list(model.processes)
# %% Import transfer coefficients

transfercoefficients_xlsx = dir_data + 'ELV_ICE_TCs.xlsx'
f.utils.import_transfercoefficients_xlsx(transfercoefficients_xlsx, model)

# check they are there for one process
smelter_cc = model.processes['smelter_cc']
list(smelter_cc.transfer_coefficients)

# %% Import flows

flows_xlsx = dir_data + 'ELV_ICE_flows.xlsx'
f.import_flows_xlsx(flows_xlsx, model)

# check that they are there
print('\nThe flows in the model are:')
list(smelter_cc.inputs)[0].to_dict()
list(smelter_cc.outputs)[0].to_dict()


for process in model.processes.values():
    print(process.name)
    for flow in process.inputs:
        print(flow.to_dict())
        model.add_flow(flow)
    for flow in process.outputs:
        model.add_flow(flow)
        print(flow.to_dict())


# %% Import matter
import futuram as f

dir_compositions = f.xlsx_to_csvs(dir_data + 'ELV_ICE_compositions.xlsx')
f.utils.import_matter_bulk(dir_compositions, model)

model.products
model.components
model.materials
model.compounds
model.elements

model.get_matter()
model.matter
model.to_dict()

dir_compositions = [os.path.join(dir_data, x) for x in os.listdir(dir_data) if 'compositions-split' in x][0]


# %% make a process flow diagram

model.flows
