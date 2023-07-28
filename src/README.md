# Futurama system model

## Installation
1. Clone the repository 
2. In the root directory of the repository, run `pip install -e ./src` to install the package in editable mode

* See src/examples/ELV to get an idea how it can work
* See classes for the different objects in the model  

## Diagram of the system model

![OverviewOfMatterClassesInTheModel](../docs/figures/Matter_classes_in_the_FutuRaM_recovery_model.png)

To do:  
* establish/connect templates for process and product data

* fix the tree map code to get the nested dicts inside the outer ones

* connect the parameters the rest of the model, 
add subclasses to parameters for the different kinds

* create efficient way to solve the model flows
