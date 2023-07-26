#%% Import the main package for the FutuRaM recovery model (other packages are imported by the main package)
import futuram as f

# Set the path to the data directory
dir_data = '../data/'

#%% CREATE THE MODEL OBJECT
#TODO: we should make a way to save and load whole models in a database or as a json file, or a set of csvs, or something.

# Create the empty model object
model = f.Model('test_system_ELV')
print(f"\n\n{'=' * 50}\n\tCreated model: {model.name}\n{'=' * 50}\n")

#%% IMPORT MATTER OBJECTS

# Take the composition datasheet (xlsx) and split its sheets into individual csvs for each type of matter
dir_compositions = f.xlsx_to_csvs(f'{dir_data}ELV_ICE_compositions.xlsx')

# Import the matter from the csvs (one fuction scans a directory, and employs the other function in the module to import each csv idividually)
f.utils.import_matter_bulk(dir_compositions, model)

## TEST:
## Uncomment to check they are there if you want
#
## FOR ALL MATTER SUBCLASSES:
print(f'\n{"-"*60}\n\t There are {len(model.list_matter())} matter objects in the model: {model.name}\n{"-"*60}\n ')
print(*model.list_matter(), sep='\n')
#
#
## FOR INDIVIDUAL MATTER SUBCLASSES:
print('\nThe elements in the model are:')
print(*model.elements, sep='\n')
print('\nThe compounds in the model are:')
print(*model.compounds, sep='\n')
print('\nThe materials in the model are:')
print(*model.materials, sep='\n')
print('\nThe components in the model are:')
print(*model.components, sep='\n')
print('\nThe products in the model are:')
print(*model.products, sep='\n')

#%%  IMPORT PROCESS OBJECTS

# Add processes from the xlsx file to the model
process_xlsx = dir_data + 'ELV_ICE_processes.xlsx'
f.utils.import_processes_xlsx(process_xlsx, model)

## TEST:
## Uncomment to check they are there if you want
#
print(f'\n{"-"*60}\n\t There are {len(model.processes)} process objects in the model: {model.name}\n{"-"*60}\n ')
print(*list(model.processes), sep='\n')

# Inspect a random process
random_process = model.processes[f.random.choice(list(model.processes.keys()))]
print(f'\n{"-"*60}\n\t  Details of random process: {random_process.name}\n{"-"*60}\n ')

table = [[k, v] for k, v in random_process.to_dict().items()]
print(f.tabulate.tabulate(table, headers=['Attribute', 'Value'], tablefmt='fancy_grid'))

# %% IMPORT FLOWS

flows_xlsx = dir_data + 'ELV_ICE_flows.xlsx'
f.import_flows_xlsx(flows_xlsx, model)

## TEST:
#TODO: embed the table outputs in the classes themselves, so that we can just call the method on the object
## Uncomment to check that they are there if you want
#
# FOR ONE PROCESS:
random_process = model.processes[f.random.choice(list(model.processes.keys()))]
print(f'\n{"-"*60}\n\t  Flows of random process: {random_process.name}\n{"-"*60}\n ')

print(f'Inputs to process {random_process.name}')
table = [[flow.name, flow.process_from, flow.process_to, flow.composition, flow.amount, flow.unit, flow.tags] for flow in random_process.inputs.values()]
print(f.tabulate.tabulate(table, tablefmt='fancy_grid', headers=['Name', 'From', 'To', 'Composition', 'Amount', 'Unit', 'Tags']))

print(f'\nOutputs from process {random_process.name}')
table = [[flow.name, flow.process_from, flow.process_to, flow.composition, flow.amount, flow.unit, flow.tags] for flow in random_process.outputs.values()]
print(f.tabulate.tabulate(table, tablefmt='fancy_grid',  headers=['Name', 'From', 'To', 'Composition', 'Amount', 'Unit', 'Tags']))

# FOR THE WHOLE MODEL:
print(f'\n{"="*60}\n\t  There are {len(model.processes.values())} flows in model {model.name}: {random_process.name}\n{"="*60}\n ')
for count, process in enumerate(model.processes.values()):
    print(f'\n{"-"*60}\n\t {count+1}/{len(model.processes.values())}. Flows of process: {process.name}\n{"-"*60}\n ')

    print(f'Inputs to process {process.name}')
    table = [[flow.name, flow.process_from, flow.process_to, flow.composition, flow.amount, flow.unit, flow.tags] for flow in process.inputs.values()]
    print(f.tabulate.tabulate(table, tablefmt='fancy_grid', headers=['Name', 'From', 'To', 'Composition', 'Amount', 'Unit', 'Tags']))

    print(f'\nOutputs from process {process.name}')
    table = [[flow.name, flow.process_from, flow.process_to, flow.composition, flow.amount, flow.unit, flow.tags] for flow in process.outputs.values()]
    print(f.tabulate.tabulate(table, tablefmt='fancy_grid',  headers=['Name', 'From', 'To', 'Composition', 'Amount', 'Unit', 'Tags']))

# %% IMPORT TRANSFER COEFFICIENTS

transfercoefficients_xlsx = dir_data + 'ELV_ICE_TCs.xlsx'
f.utils.import_transfercoefficients_xlsx(transfercoefficients_xlsx, model)

## TEST:
## Uncomment to check they are there for one random process if you want
# (btw. markets have no transfer coefficients)
random_process = model.processes[f.random.choice(list(model.processes.keys()))]
print(f'\n\n{"-"*60}\n   Transfer coefficients for random process: {random_process.name}\n{"-"*60}')
table = [[d['input'], d['output'], d['transfer_coefficient'], d['uncertainty']] for d in random_process.transfer_coefficients.values()]
if len(table) > 0:
    print(f.tabulate.tabulate(table, headers=list(list(random_process.transfer_coefficients.values())[0].keys()), tablefmt='fancy_grid'))
else:
    print(f'No transfer coefficients for process {random_process.name}')

# %% CALCULATE THE QUANTITIES OF FLOWS IN THE MODEL


# %% VISUALISE THE MODEL

#%% INDIVIDUAL PROCESSES

# Create isolated flowcharts for each process in the model, showing only the process and its direct inputs and outputs

print(f'\n{"="*80}\n Making isolated flow charts for the {len(model.processes.values())} processes in model \'{model.name}\'\n{"="*80}\n')
for count, proc in enumerate(model.processes.values()):
    print(f'{count+1}/{len(model.processes.values())}.')
    f.make_flowchart(proc)

#%% WHOLE MODEL

# Create a flowchart for the whole model, showing all processes and their inputs and outputs
f.make_flowchart(model)

#%% FILTERED FLOWCHARTS

# Create flowcharts for the whole model based on filters (eg: [WS=='ELV'], or ['market' in process.tags] etc.)

#TODO: still need to implement this, just an adaption of the above flowchart function

#%% MATTER FLOWCHARTS

# Create flowcharts for the whole model based on matter (eg: [matter.name=='steel'], or ['iron' in matter.tags] etc.)

#TODO: still need to write this

# %% THE END


#%% VALIDATE THE MODEL
f.validate_model(model)
 

#%% TESTING FOR MAKING THE FUNCTION TO CHANGE THE FLOW AMOUNTS

# initial processes
process = model.processes['dismantling_ICE']

# set input
waste_input = dismantling_ICE.inputs['collection_ICE_to_dismantling_ICE']
waste_input.amount = 1000
waste_input.unit = 'kg'
waste_input.to_dict()


fractions_out = [flow.to_dict() for flow in process.outputs.values()]

fractions_in = [model.matter[flow.composition].composition for flow in process.inputs.values()]

for flow in process.inputs.values():
    amount = flow.amount
    flow_composition_in = model.matter[flow.composition].composition
    for fraction in flow_composition_in.values():
        fraction['amount'] = amount * fraction['mass_fraction']
    flow.fractions = flow_composition_in

for flow_out in process.outputs.values():
    for flow_in in process.inputs.values():
        
        try:
            flow_out.amount = flow_in.fractions[flow_out.composition]['amount']*float(process.transfer_coefficients[flow_out.composition]['transfer_coefficient'])
            print(flow_out.amount)
        except KeyError as e:
             print(e)
             pass
    
