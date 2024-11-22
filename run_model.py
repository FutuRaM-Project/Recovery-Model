import pandas as pd
from src.recovery_model import RecoveryModel

pd.set_option("multi_sparse", False)
pd.set_option("display.float_format", "{:.2f}".format)



data_folder = "data_folder/test_2"

model = RecoveryModel(
    data_folder=data_folder,
)

print(model.solve())