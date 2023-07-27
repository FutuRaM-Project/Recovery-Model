#%% Import the main package for the FutuRaM recovery model (other packages are imported by the main package)
import futuram as f
test = True
# Set the path to the data directory
dir_data = '../data/'

#%% CREATE THE MODEL OBJECT

# Create the empty model object
model = f.Model('test_system_ELV')

#%% IMPORT MATTER OBJECTS

# Take the composition xlsx and split it into csvs for each sheet
dir_compositions = f.xlsx_to_csvs(f'{dir_data}ELV_ICE_compositions.xlsx')

# Import the matter from the csvs 
f.utils.import_matter_bulk(dir_compositions, model)

# Test to see if it worked:
model.print_matter_subclasses()

#%%  IMPORT PROCESS OBJECTS

# Add processes from the xlsx file to the model
process_xlsx = dir_data + 'ELV_ICE_processes.xlsx'
f.utils.import_processes_xlsx(process_xlsx, model)

## TEST
if test:
    model.print_processes()
    # Inspect a random process
    model.random_process().print_table()

#%% IMPORT FLOWS

flows_xlsx = dir_data + 'ELV_ICE_flows.xlsx'
f.import_flows_xlsx(flows_xlsx, model)

## TEST
if test:
    # FOR ONE PROCESS:
    model.random_process().print_flows()
    # FOR THE WHOLE MODEL:
    model.print_flows()

# %% IMPORT TRANSFER COEFFICIENTS

transfer_coefficients_xlsx = dir_data + 'ELV_ICE_TCs.xlsx'
f.utils.import_transfercoefficients_xlsx(transfer_coefficients_xlsx, model)

## TEST:
if test:
    # FOR ONE PROCESS
    model.random_process().print_transfer_coefficients()
    # FOR THE WHOLE MODEL
    model.print_transfer_coefficients()

#%% VALIDATE THE MODEL
f.validate_model(model)

#%% CALCULATE THE QUANTITIES OF FLOWS IN THE MODEL

# set input
waste_input = model.processes['collection_ICE'].inputs['PutOnMarket_ICE_to_collection_ICE']
waste_input.to_dict()
waste_input.set_amount(1000)
waste_input.to_dict()
model.print_flows()

for flow in model.get_flows().values():
    flow.calculate_amount(model)
# calculate to

#%% VISUALISE THE MODEL

## INDIVIDUAL PROCESSES
# Create isolated flowcharts for each process in the model, showing only the process and its direct inputs and outputs

model.make_process_flowcharts()

#% WHOLE MODEL

# Create a flowchart for the whole model, showing all processes and their inputs and outputs
model.make_flowchart_model()
model.make_process_network()

#%% FILTERED FLOWCHARTS

# Create flowcharts for the whole model based on filters (eg: [WS=='ELV'], or ['market' in process.tags] etc.)

#TODO: still need to implement this, just an adaption of the above flowchart function

#%% MATTER FLOWCHARTS

# Create flowcharts for the whole model based on matter (eg: [matter.name=='steel'], or ['iron' in matter.tags] etc.)

#TODO: still need to write this

# %% THE END



 
#%% TESTING FOR MAKING THE FUNCTION TO CHANGE THE FLOW AMOUNTS


# waste_input.amount = 1000
# waste_input.unit = 'kg'
# waste_input.to_dict()



# fractions_out = [flow.to_dict() for flow in process.outputs.values()]

# fractions_in = [model.matter[flow.composition].composition for flow in process.inputs.values()]

# for flow in process.inputs.values():
#     amount = flow.amount
#     flow_composition_in = model.matter[flow.composition].composition
#     for fraction in flow_composition_in.values():
#         fraction['amount'] = amount * fraction['mass_fraction']
#     flow.fractions = flow_composition_in

# for flow_out in process.outputs.values():
#     for flow_in in process.inputs.values():
        
#         try:
#             flow_out.amount = flow_in.fractions[flow_out.composition]['amount']*float(process.transfer_coefficients[flow_out.composition]['transfer_coefficient'])
#             print(flow_out.amount)
#         except KeyError as e:
#              print(e)
#              pass
    


f.make_flowchart(model)