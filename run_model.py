import warnings
import pandas as pd
from recovery_model_LA import RecoveryModelLA
from recovery_model_optimized import RecoveryModelOptimized
from pandas.errors import SettingWithCopyWarning

pd.set_option('future.no_silent_downcasting',True)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
pd.set_option("multi_sparse", False)
pd.set_option("display.float_format", "{:.2f}".format)



data_folder = "data_folder/test_weee"
layer_names = ['product','component','material','element']
recovery_model = RecoveryModelOptimized

model = recovery_model(
    data_folder=data_folder,
    layer_names=layer_names
)

print(model.solve_models_and_write_to_output())