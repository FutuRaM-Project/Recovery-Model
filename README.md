# Futuram Recovery Model

## Table of Contents

This repository contains:  
- `doc/` the documentation about recovery model  
- `src/` the source code of the recovery model  
- `data_folder/` mock data to test the model  



## Using this model

To use the model, you can add a new folder to 'data_folder' and add 4 files to the input_data folder in that folder:
- inflows.csv -- Defines the inflows per resource
- composition.csv -- Defines the composition of each resource
- TCs.csv -- Defines the transfer coefficients

Then, specify your data folder in the run_model.py or run_model.ipynb file and execute it. Your data will be saved to an output folder within the folder you created.
The definitions for how these tables should be formatted can be found in /doc/user_guide.docx. 
