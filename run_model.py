import warnings
import pandas as pd
from src.recovery_model import RecoveryModel
from pandas.errors import SettingWithCopyWarning

pd.set_option('future.no_silent_downcasting',True)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
pd.set_option("multi_sparse", False)
pd.set_option("display.float_format", "{:.2f}".format)



data_folder = "data_folder/basic_test"
layer_names = ['product','component','material','element']

model = RecoveryModel(
    data_folder=data_folder,
    layer_names=layer_names
)

print(model.solve_models_and_write_to_output())