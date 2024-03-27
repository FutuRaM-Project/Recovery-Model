# Futuram Recovery Model

## Table of Contents

This repository contains:  
- `doc/` the documentation about recovery model  
- `src/` the source code of the recovery model  
- `data/` mock data to test the model  
- `results/` the results obtained when running the model
- `consolidation/` intermediary file to ensure consistency of the model inputs
- `performance/`  additional files to investigate the recovery model performances


## To Do list

- [] enable viewing subset of the recovery model matrix
- [] write routine for mass balance check:
  - [] for the composition
  - [] for the entire system
- [] define priority rules in case of conflicts accross TCs (?)
- [] enable to divide the system into sub-system that can be solved sequentially
- [] Define how uncertainty and data quality should be propagated