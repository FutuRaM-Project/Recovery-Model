# Futurama system model

## Installation
1. Clone the repository 
2. Run 
   > bash auto_install.sh to install everything (may require 'chmod +x auto_install.sh' first)
   Or
   >In the root directory of the repository, run `pip install -e ./src` to install the package in editable mode

* See src/examples/ELV to get an idea how it can work
* See classes for the different objects in the model

## Overview of the classes in system model
![OverviewOfClassesInTheModel](../docs/figures/OverviewOfClassesInTheModel.svg)

## Overview of matter classes in the model
![OverviewOfMatterClassesInTheModel](../docs/figures/Matter_classes_in_the_FutuRaM_recovery_model.png)

To do:  
* establish/connect templates for process and product data

* fix the tree map code to get the nested dicts inside the outer ones

* connect the parameters the rest of the model, 
add subclasses to parameters for the different kinds

* create efficient way to solve the model flows
