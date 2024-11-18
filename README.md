# Futuram Recovery Model

## Table of Contents

This repository contains:  
- `doc/` the documentation about recovery model  
- `src/` the source code of the recovery model  
- `data_folder/` mock data to test the model  



## Using this model

To use the model, you can add a new folder to 'data_folder' and add 4 files to the input_data folder in that folder:
- metadata.csv -- A metadata file containing the information of what flows and resources are defined
- inflows.csv -- Defines the inflows per resource
- composition.csv -- Defines the composition of each resource
- TCs.csv -- Defines the transfer coefficients


## To Do list

- [ ] write routine for mass balance check:
  - [ ] for the composition
  - [ ] for the entire system
- [ ] define priority rules in case of conflicts accross TCs (?)
- [ ] enable to divide the system into sub-system that can be solved sequentially
- [ ] Define how uncertainty and data quality should be propagated