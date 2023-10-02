"""
Configuration file for the project.

Use this file to declare variables that are used throughout the project.

eg. data directories, file names, etc.

"""
    

from pathlib import Path


    # Define some common variables
    
WS_names = ['BATT', 'ELV', 'MIN', 'WEEE', 'SLASH', 'CDW']
        
    # Define the directories of the project
DIR_REPO = Path(__file__).resolve().parents[3]

DIR_SRC = DIR_REPO / 'src'
DIR_DOCS = DIR_REPO / 'docs'

DIR_DATA = DIR_SRC / 'data'
DIR_EXAMPLES = DIR_SRC / 'examples'
DIR_TESTS = DIR_SRC / 'tests'

DIR_CODELISTS = DIR_DATA / 'codelists'

# define the data files

CODELIST_PROCESSES = DIR_CODELISTS / 'FutuRaM_process_codelists.xlsx'

CODELIST_MATTER = DIR_CODELISTS / 'FutuRaM_codelists_repository.xlsx'

LIST_STOCKSANDFLOWS = DIR_DATA / 'listOfStocksAndFlows.xlsx'
