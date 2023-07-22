#%%
import os
import sys

# Add the path to the Integrated model folder to the system path
sys.path.insert(0, '/home/stew/code/gh/futuram/IntegratedModel')

# import the function
from utils.split_xlsx_to_csvs import xlsx_to_csvs

# %%
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

xlsx_to_csvs('../../data/ELV_ICE_compositions.xlsx')
# %%
