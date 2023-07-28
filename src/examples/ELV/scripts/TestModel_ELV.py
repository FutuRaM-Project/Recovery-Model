'''
TestModel_ELV.py

This is a test script to import dummy ELV data and 
run the model.

Steps:
    1. Import the main package for the FutuRaM recovery model
    2. Create the model object
    3. Import matter objects
    4. Import process objects
    5. Import flows
    6. Import transfer coefficients
    7. Validate the model
    8. Calculate the quantities of flows in the model
    9. Visualise the model
    10. The end

Dependencies:
    futuram
'''

# %% Import the main package for the FutuRaM recovery model
# (other packages are imported by the subpackages and their modules)
import futuram as f

# toggle test mode to print out more information
TEST = True

# Set the path to the data directory
DIR_DATA = "../data/"

# %% CREATE THE MODEL OBJECT

# Create the empty model object
model = f.classes.Model("TestModel_ELV")

# %% IMPORT MATTER OBJECTS

# Take the composition xlsx and split it into csvs for each sheet
DIR_COMPOSITIONS = f.utils.xlsx_to_csvs(f"{DIR_DATA}ELV_ICE_compositions.xlsx")

# Import the matter from the csvs
f.utils.import_matter_bulk(DIR_COMPOSITIONS, model)

# Test to see if it worked:
model.print_matter_subclasses()

# %%  IMPORT PROCESS OBJECTS

# Add processes from the xlsx file to the model
PROCESS_XLSX = DIR_DATA + "ELV_ICE_processes.xlsx"
f.utils.import_processes_xlsx(PROCESS_XLSX, model)

## TEST
if TEST:
    print("\n\n A random process:")
    model.random_process().print_table()
    print("\n\n All processes in the model:")
    model.print_processes()
    # Inspect a random process

# %% IMPORT FLOWS

FLOWS_XLSX = DIR_DATA + "ELV_ICE_flows.xlsx"
f.utils.import_flows_xlsx(FLOWS_XLSX, model)

## TEST
if TEST:
    # FOR ONE PROCESS:
    print("\n\n A random process:")
    model.random_process().print_flows()
    # FOR THE WHOLE MODEL:
    print("\n\n All flows in the model:")
    model.print_flows()

# %% IMPORT TRANSFER COEFFICIENTS

TRANSFER_COEFFICIENTS_XLSX = DIR_DATA + "ELV_ICE_TCs.xlsx"
f.utils.import_transfercoefficients_xlsx(TRANSFER_COEFFICIENTS_XLSX, model)

## TEST:
if TEST:
    # FOR ONE PROCESS
    print("\n\n A random process:")
    model.random_process().print_transfer_coefficients()
    # FOR THE WHOLE MODEL
    print("\n\n All transfer coefficients in the model:")
    model.print_transfer_coefficients()

# %% VALIDATE THE MODEL
f.utils.validate_model(model)

# %% CALCULATE THE QUANTITIES OF FLOWS IN THE MODEL

# set input
waste_input = model.processes["collection_ICE"].inputs[
    "PutOnMarket_ICE_to_collection_ICE"
]
waste_input.to_dict()
waste_input.set_amount(1000)
waste_input.to_dict()
model.print_flows()

for flow in model.get_flows().values():
    flow.calculate_amount(model)
# calculate to

# %% VISUALISE THE MODEL

## INDIVIDUAL PROCESSES
# Create isolated flowcharts for each process in the model,
# showing only the process and its direct inputs and outputs

model.make_flowchart_processes()

# % WHOLE MODEL

# Create a flowchart for the whole model, showing
# all processes and their inputs and outputs

model.make_flowchart_model()
model.make_network()

# %% FILTERED FLOWCHARTS

# Create flowcharts for the whole model based on filters
# (eg: [WS=='ELV'], or ['market' in process.tags] etc.)

# TODO: still need to implement this, just an adaption of the above flowchart function

# %% MATTER FLOWCHARTS

# Create flowcharts for the whole model based on matter
# (eg: [matter.name=='steel'], or ['iron' in matter.tags] etc.)

# TODO: still need to write this

# %% THE END
print(f"\n\n{'='*90}\n\t {'FIN '*10} \n{'='*90}\n")

# %% TESTING FOR MAKING THE FUNCTION TO CHANGE THE FLOW AMOUNTS


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
