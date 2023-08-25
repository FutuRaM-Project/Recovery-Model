#cd C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_ELV\src\Stock_recycling_ELV\recycling
# pip install .

import sys
sys.path.append("C:\\Users\\deepj\\OneDrive - Chalmers\\Deep_FutuRaM\\Models\\IntegratedModel_recycling\\recycling_package\\recycling")
print(sys.path)
sys.path


from recycling.core import process_composition_data

input_path = r"C:\Users\deepj\OneDrive - Chalmers\Deep_FutuRaM\Models\IntegratedModel_ELV\src\examples\ELV\data\Stock_model\composition.xlsx"
start_year = 2000  # Specify the start year here
end_year = 2003    # Specify the end year here

process_composition_data(input_path, start_year, end_year)
    