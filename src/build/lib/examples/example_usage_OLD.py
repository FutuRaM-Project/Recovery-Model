
#%% 0. IMPORT MODULES

# Import classes
from classes.classes_matter import Element, Compound, Material, Component, Product
from classes.classes_processes import Process
from classes.classes_flows import Flow
from classes.classes_parameters import Scenario, Parameter
from classes.classes_model import Model

#%% 1.  BUILD A PRODUCT SYSTEM


model = Model("test_model")

# define some elements (can also be done directly in the material definition)
Ti = Element('Ti')
C = Element('C')

Ti.expand_composition()
Ti.composition_expanded

elements = [Ti, C]
for element in elements: element.add_to_model(model)

# create a compound from a formula (can also be done via the element class)
ironoxide = Compound("Iron (III) oxide", {"Fe": 2, "O": 3})
plastic = Compound("Plastic", {"C": 100, "H": 200, "Cl": 1})
rubber = Compound("Rubber", {"C": 500, "H": 800, "S": 13, "Cl": 2})

# ironoxide._create_treemap_data()
# rubber.create_treemap()

compounds = [ironoxide, plastic, rubber]
for compound in compounds: compound.add_to_model(model)

# create a material from a list of components
steel_ti = Material("Steel (Ti)", {ironoxide : 0.9, Ti : 0.04, C : 0.06})
steel_mild = Material("Steel (mild)", {ironoxide : 0.9, C : 0.1})

steel_ti.tags += ["steel", "Ti", "alloy", "metal", "ELV", ]
steel_mild.tags += ["steel", "mild", "alloy", "metal", "ELV", ]


steel_ti.expand_composition()
steel_ti.composition_expanded_to_json()
# steel_ti.create_treemap()
# steel_mild.create_treemap()

materials = [steel_ti, steel_mild]
for material in materials: material.add_to_model(model)

# create a component from a material and a compound
wheel = Component("Wheel", {rubber : 0.2, steel_ti : 0.8})
body = Component("Body", {plastic : 0.3, steel_mild : 0.7})

# body._create_treemap_data()
# body.create_treemap()

components = [wheel, body]
for component in components: component.add_to_model(model)

# create a product from a list of components
car = Product("Piaggio Ape", {wheel: 0.1, body: 0.9})
car.tags += ["car", "vehicle", "transportation", "ELV", ]
# look at the car
car.to_dict()
car.add_to_model(model)

car.expand_composition()
car.composition 
# car.create_treemap()

products = [car]

js = car.composition_expanded_json


print(js)


car.expand_composition()
# car.create_treemap()
# look at the model
model.to_dict()

#%% 2. MAKE A PROCESS TO SHRED THE CAR
# Create a process with description and tags
shred = Process("Car shredder", "This is a unit process that represents the shredding of a car", ["physical", "shredding"])
collection = Process("Collection", "This is a unit process that represents the collection of a car", ["physical", "collection"])

# add some flows to get the stuff back out
shred.WS = "ELV"


flow_CarToShred = Flow("car for shredding", to=shred, from_=collection, amount=1, unit="car")
flow_CarToShred.composition = car.composition

flow_CarShredded_metal = Flow("metal from shredded car", to='X', from_=shred, amount=900, unit="kg")
flow_CarShredded_metal.tags += ["metal", "ELV", 'ferrous']
#! need to make a way to add and remove materials from a flow
flow_CarShredded_metal.composition = steel_ti.composition # + steel_mild.composition
flow_CarShredded_metal.amount = 900 # should be: amount of metal in the car * transfer coefficient

flow_CarShredded_metal.to_dict()

flow_CarShredded_plastic = Flow("shredded car plastic", to='Y', from_=shred, amount=100, unit="kg")

#! processes can take flows or matters as inputs and outputs (maybe should be limited to flows?)

# shred.add_input(car)
# shred.add_output(steel_ti)
# shred.add_output(steel_mild)
# shred.add_output(rubber)
# shred.add_output(plastic)

shred.add_input(flow_CarToShred)
shred.add_output(flow_CarShredded_metal)
shred.add_output(flow_CarShredded_plastic)

shred.to_dict()

# add a parameter to the process to represent the efficiency (default is 1)

#! need to make a way to transform using the parameter, eg. amount * efficiency --> then the rest is waste, or a different flow, something like that
shred.add_parameter("efficiency")

shred.to_dict()

from visualisation.make_PFD import create_process_diagram

create_process_diagram(shred)


## UP TO HERE IS IS WORKING FINE 
#%% Make a process to recycle the steel

# Create a process with description and tags
recycle_steel = Process("Steel recycling", "This is a unit process that represents the recycling of steel", ["physical", "recycling", "pyrometallurgy"])
ocean_dumping = Process("Ocean dumping", "This is a unit process that represents the dumping of plastic in the ocean", ["physical", "dumping", "ocean"])

# Create flows
flow_CarShredded_metal = Flow("steel_from_shredder", to=recycle_steel, from_=shred, amount=1, unit="kg")
flow_CarShredded_metal.composition = {"Fe": 0.9, "C": 0.1}


flow_CarShredded_plastic = Flow("plastic_from_shredder", to=ocean_dumping, from_=shred, amount=1, unit="kg")
flow_CarShredded_plastic.composition = plastic.composition

flow_recycled_steel = Flow("recycled_steel", to='X', from_=recycle_steel, amount=0.9, unit="kg")
flow_recycled_steel.composition = steel_mild.composition


ocean_dumping.add_input(flow_CarShredded_plastic)
create_process_diagram(ocean_dumping)


# Create parameters with definition, uncertainty, and data sources
parameter_1 = Parameter("Parameter 1", description="This parameter represents the conversion efficiency of the process.")
parameter_1.uncertainty = 0.05
parameter_1.add_data_source("Research paper")
parameter_1.add_data_source("Internal experimental data")

parameter_2 = Parameter("Parameter 2", description="This parameter represents the energy consumption of the process.")
parameter_2.uncertainty = 0.1
parameter_2.add_data_source("Energy audit report")

# Link objects
recycle_steel.add_input(flow_CarShredded_metal)
recycle_steel.add_output(flow_recycled_steel)
recycle_steel.add_parameter(parameter_1)
recycle_steel.add_parameter(parameter_2)
recycle_steel.to_dict()

for flow in recycle_steel.inputs:
    print(flow.name)
    print(flow.composition)
for flow in recycle_steel.outputs:
    print(flow.name)
    print(flow.composition)

# Access object attributes
print(recycle_steel.name)  # Output: Process 1
print(recycle_steel.description)  # Output: This is a unit process that converts raw material to finished product.
print(recycle_steel.tags)  # Output: ['chemical', 'reaction']

# Access linked objects
print(recycle_steel.inputs)  # Output: [flow_1]
print(recycle_steel.outputs)  # Output: [flow_2]
print(recycle_steel.parameters)  # Output: [parameter_1, parameter_2]

# Access parameter attributes
print(parameter_1.name)  # Output: Parameter 1
print(parameter_1.description)  # Output: This parameter represents the conversion efficiency of the process.

for obj in [recycle_steel, ocean_dumping, flow_CarShredded_metal, flow_CarShredded_plastic, flow_recycled_steel, parameter_1, parameter_2]:
    print(obj.name)
    obj.add_to_model(model)

# Example usage:

# Create scenarios
scenario_bau = Scenario("Scenario_BAU")
scenario_rec = Scenario("Scenario_REC")
scenario_cir = Scenario("Scenario_CIR")

scenario_bau.set_description("Business as usual")
scenario_rec.set_description("Recovery")
scenario_cir.set_description("Circularity")

scenario_bau.to_dict()