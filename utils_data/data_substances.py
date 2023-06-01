
#%% DATA FOR ELEMENTS
import periodictable as pt
import pandas as pd
import numpy as np
import os

os.getcwd()

list = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cf', 'Cl', 'Cm', 'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fl', 'Fm', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Lv', 'Mc', 'Md', 'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Nh', 'Ni', 'No', 'Np', 'O', 'Og', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm', 'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'Ts', 'U', 'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']
#%% DATA FOR ELEMENTS
import periodictable as pt
import pandas as pd
import numpy as np
import os

os.getcwd()

from tabulate import tabulate

elements = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cf', 'Cl', 'Cm', 'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fl', 'Fm', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Lv', 'Mc', 'Md', 'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Nh', 'Ni', 'No', 'Np', 'O', 'Og', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm', 'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'Ts', 'U', 'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

commercially_important = [
    False, True, True, False, False, False, False, True, False, True, False, False, False, False, False, False, True, True,
    False, False, False, False, False, True, True, False, True, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, True, True, True, False, False, False, False, True, False, False, True,
    False, False, False, False, True, False, False, False, False, False, True, True, False, False, False, False, False,
    False, False, False, False, True, False, False, False, False, False, False, True, False, False, False, False, False,
    False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False,
    True, False
]

toxic_elements = ['Hg', 'Pb', 'Cd', 'As', 'Cr', 'Ni', 'Co', 'Cu', 'Zn', 'Mn', 'Sb', 'Se', 'Be', 'Tl', 'Ag', 'Au', 'Bi', 'Te']

#%%

element_health = {
    'hydrogen': False,
    'helium': False,
    'lithium': False,
    'beryllium': True,
    'boron': False,
    'carbon': False,
    'nitrogen': False,
    'oxygen': False,
    'fluorine': True,
    'neon': False,
    'sodium': True,
    'magnesium': False,
    'aluminum': True,
    'silicon': False,
    'phosphorus': False,
    'sulfur': False,
    'chlorine': True,
    'argon': False,
    'potassium': True,
    'calcium': False,
    'scandium': False,
    'titanium': False,
    'vanadium': False,
    'chromium': False,
    'manganese': False,
    'iron': False,
    'cobalt': False,
    'nickel': False,
    'copper': False,
    'zinc': False,
    'gallium': False,
    'germanium': False,
    'arsenic': True,
    'selenium': True,
    'bromine': True,
    'krypton': False,
    'rubidium': True,
    'strontium': False,
    'yttrium': False,
    'zirconium': False,
    'niobium': False,
    'molybdenum': False,
    'technetium': True,
    'ruthenium': False,
    'rhodium': False,
    'palladium': False,
    'silver': False,
    'cadmium': True,
    'indium': True,
    'tin': True,
    'antimony': True,
    'tellurium': True,
    'iodine': True,
    'xenon': False,
    'cesium': True,
    'barium': False,
    'lanthanum': False,
    'cerium': False,
    'praseodymium': False,
    'neodymium': False,
    'promethium': True,
    'samarium': False,
    'europium': False,
    'gadolinium': False,
    'terbium': False,
    'dysprosium': False,
    'holmium': False,
    'erbium': False,
    'thulium': False,
    'ytterbium': False,
    'lutetium': False,
    'hafnium': False,
    'tantalum': False,
    'tungsten': False,
    'rhenium': False,
    'osmium': False,
    'iridium': False,
    'platinum': False,
    'gold': False,
    'mercury': True,
    'thallium': True,
    'lead': True,
    'bismuth': False,
    'polonium': True,
    'astatine': True,
    'radon': True,
    'francium': True,
    'radium': True,
    'actinium': True,
    'thorium': True,
    'protactinium': True,
    'uranium': True,
    'neptunium': True,
    'plutonium': True,
    'americium': True,
    'curium': True,
    'berkelium': True,
    'californium': True,
    'einsteinium': True,
    'fermium': True,
    'nobelium': True,
    'lawrencium': True,
    'rutherfordium': True,
    'dubnium': True,
    'bohrium': True,
    'hassium': True,
    'meitnerium': True,
    'darmstadtium': True,
    'roentgenium': True,
    'copernicium': True,
    'nihonium': True,
    'flerovium': True,
    'livermorium': True,
    'tennessine': True,
    'oganesson': True
}

a = pd.DataFrame.from_dict(element_health, orient='index', columns=['health'])

#%%

table = [['Element', 'Commercially Important']]
for element, important in zip(elements, commercially_important):
    table.append([element, str(important)])

print(tabulate(table, headers="firstrow", tablefmt="grid"))











#%%

e_list = []
for e in list:
    e = pt.elements.symbol(e)
    e_tuple = (e.symbol, e.name, e.number, e.mass)
    e_list.append(e_tuple)

e_df = pd.DataFrame(e_list, columns=['code', 'name', 'atomic_number', "atomic_mass"]).sort_values(by='code', ascending=True)

crms = pd.read_csv('../data/list_crms.csv', sep=';')
crms = crms.apply(lambda x: x.astype(str).str.lower())
crms = crms.apply(lambda x: x.astype(str).str.strip())


merge = pd.merge(e_df, crms, how='left', left_on='name', right_on='name')
merge.replace(np.NaN, False, inplace=True)
merge.replace('false', False, inplace=True)
merge.replace('true', True, inplace=True)

price = pd.read_csv('../data/price_elements.csv', sep=';')
merge = pd.merge(merge, price, how='left', left_on='code', right_on='code')

merge.to_csv('../data/list_elements.csv', index=False)


#%% Data for compounds and materials from EI

import bw2data as bd
import pandas as pd

bd.projects.set_current('futurama')

ei = bd.Database('con391')

acts_all = pd.DataFrame([x.as_dict() for x  in ei])
    # pull out and look at the categories (this is slow, there must be a better way to pull the list of tuples out into columns...)
print("Extracting classification data")
acts_all["ISIC"] = ''
acts_all["CPC"] = ''
for i, j in acts_all.iterrows():
    try:
        for k in j["classifications"]:
            if "ISIC" in k[0]:
                acts_all.loc[i,'ISIC'] = k[1].split(":")[0]
                acts_all.loc[i,'ISIC_name'] = k[1].split(":")[1]
            if "CPC" in k[0]:
                acts_all.loc[i,'CPC'] = k[1].split(":")[0]
                acts_all.loc[i,'CPC_name'] = k[1].split(":")[1]
    except:
        print(f"ERROR: {j['id'], j['classifications']}")
        # act = bd.get_node(id=j['id'])
        # act.delete()
        continue

acts_all = acts_all.drop("classifications", axis=1)

acts_all = acts_all[
    (acts_all['location'].apply(lambda x: True if any(i in x for i in ['GLO', 'RoW']) else False))
    & (acts_all['unit'] == 'kilogram')
    ]
# Filter by CPC codes
acts_all["prod_category"] = ""
acts_all["prod_sub_category"] = ""
for i, j in acts_all.iterrows():

    cpc = acts_all.at[i, "CPC"].split(":")[0]
    if len(cpc) < 5:
        cpc += "0"*(5-len(cpc))
    cpc = int(cpc)

    if (cpc in range(0,2000) or cpc in range (3000, 4000)):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Agricultural and forestry products"
    if (cpc in range(2000,3000) or cpc in range (4000, 5000)):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Live animal, fish and their products"
    if cpc in range(11000,18000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(18000,19000):
        acts_all.at[i, "prod_category"] = "Chemical"
        acts_all.at[i, "prod_sub_category"] = "Chemical products"
    if cpc in range(21000,24000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Food & beverages, animal feed"
    if cpc in range(26000,28200):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Textile"
    if cpc in range(31000,32000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Wood, straw & cork"
    if cpc in range(32000,33000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Pulp & paper"
    if cpc in range(33000,34000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(34000,36000):
        acts_all.at[i, "prod_category"] = "Chemical"
        acts_all.at[i, "prod_sub_category"] = "Chemical products"
    if cpc in range(34700,34800):
        acts_all.at[i, "prod_category"] = "PlastRub"
        acts_all.at[i, "prod_sub_category"] = "Plastics & rubber products"
    if cpc in range(35500,37000):
        acts_all.at[i, "prod_category"] = "PlastRub"
        acts_all.at[i, "prod_sub_category"] = "Plastics & rubber products"
    if cpc in range(37000,38000):
        acts_all.at[i, "prod_category"] = "GlasNonMetal"
        acts_all.at[i, "prod_sub_category"] = "Glass and other non-metallic products"
    if cpc in range(39000,40000):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Agricultural and forestry products"
    if cpc in range(40000,42000):
        acts_all.at[i, "prod_category"] = "MetalAlloy"
        acts_all.at[i, "prod_sub_category"] = "Basic metals & alloys, their semi-finished products"
    if cpc in range(42000,43000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Food & beverages, animal feed"
    if cpc in range(43000,49000):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Metal/electronic equipments and parts"
    if cpc in range(49000,49400):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Transport vehicles"
    if cpc in range(49000,49915):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Transport vehicles"
    if cpc in range(49941,50000):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Metal/electronic equipments and parts"
    if cpc in range(60000,70000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(88000,90000):
        acts_all.at[i, "prod_category"] = "MetalAlloy"
        acts_all.at[i, "prod_sub_category"] = "Basic metals & alloys, their semi-finished products"
    if cpc == 38100: #wooden furniture
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Wood, straw & cork"
    if cpc == 38450: #fishing stuff
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Textile"



FM_cats = ["OreMinFuel", "Chemical", "PlastRub", "GlasNonMetal", "MetalAlloy", "MachElecTrans"]
acts_FM = acts_all[acts_all.prod_category.isin(FM_cats)]
acts_FM = acts_FM[['name', 'reference product',  "ISIC_name", "ISIC", "CPC_name", "CPC","prod_category", "prod_sub_category", "code", 'activity type']]
acts_FM.rename(columns={"code": "code_EI"}, inplace=True)

substances_FM = acts_FM[acts_FM["activity type"] == "market activity"]
processes_FM = acts_FM[acts_FM["activity type"] == "ordinary transforming activity"]

acts_FM.to_csv('data/activities_from_ei_con319.csv', index=False)
substances_FM.to_csv('data/substances_from_ei_con319.csv', index=False)
processes_FM.to_csv('data/processes_from_ei_con319.csv', index=False)




# isic = [x.split(":") for x in acts_all.ISIC.unique()]
# isic = [x[1] for x in isic if len(x) == 2]
# isic.sort()
# print("\t# of ISIC categories:", len(isic))
# cpc =  acts_all.CPC.unique().tolist()
# cpc.sort()
# print("\t# of CPC categories:", len(cpc))

]


e_list = []
for e in pt.elements:
    e_tuple = (e.symbol, e.name, e.number, e.mass)
    e_list.append(e_tuple)

e_df = pd.DataFrame(e_list, columns=['code', 'name', 'atomic_number', "atomic_mass"]).sort_values(by='code', ascending=True)

crms = pd.read_csv('../data/list_crms.csv', sep=';')
crms = crms.apply(lambda x: x.astype(str).str.lower())
crms = crms.apply(lambda x: x.astype(str).str.strip())


merge = pd.merge(e_df, crms, how='left', left_on='name', right_on='name')
merge.replace(np.NaN, False, inplace=True)
merge.replace('false', False, inplace=True)
merge.replace('true', True, inplace=True)

price = pd.read_csv('../data/price_elements.csv', sep=';')
merge = pd.merge(merge, price, how='left', left_on='code', right_on='code')

merge.to_csv('../data/list_elements.csv', index=False)


#%% Data for compounds and materials from EI

import bw2data as bd
import pandas as pd

bd.projects.set_current('futurama')

ei = bd.Database('con391')

acts_all = pd.DataFrame([x.as_dict() for x  in ei])
    # pull out and look at the categories (this is slow, there must be a better way to pull the list of tuples out into columns...)
print("Extracting classification data")
acts_all["ISIC"] = ''
acts_all["CPC"] = ''
for i, j in acts_all.iterrows():
    try:
        for k in j["classifications"]:
            if "ISIC" in k[0]:
                acts_all.loc[i,'ISIC'] = k[1].split(":")[0]
                acts_all.loc[i,'ISIC_name'] = k[1].split(":")[1]
            if "CPC" in k[0]:
                acts_all.loc[i,'CPC'] = k[1].split(":")[0]
                acts_all.loc[i,'CPC_name'] = k[1].split(":")[1]
    except:
        print(f"ERROR: {j['id'], j['classifications']}")
        # act = bd.get_node(id=j['id'])
        # act.delete()
        continue

acts_all = acts_all.drop("classifications", axis=1)

acts_all = acts_all[
    (acts_all['location'].apply(lambda x: True if any(i in x for i in ['GLO', 'RoW']) else False))
    & (acts_all['unit'] == 'kilogram')
    ]
# Filter by CPC codes
acts_all["prod_category"] = ""
acts_all["prod_sub_category"] = ""
for i, j in acts_all.iterrows():

    cpc = acts_all.at[i, "CPC"].split(":")[0]
    if len(cpc) < 5:
        cpc += "0"*(5-len(cpc))
    cpc = int(cpc)

    if (cpc in range(0,2000) or cpc in range (3000, 4000)):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Agricultural and forestry products"
    if (cpc in range(2000,3000) or cpc in range (4000, 5000)):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Live animal, fish and their products"
    if cpc in range(11000,18000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(18000,19000):
        acts_all.at[i, "prod_category"] = "Chemical"
        acts_all.at[i, "prod_sub_category"] = "Chemical products"
    if cpc in range(21000,24000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Food & beverages, animal feed"
    if cpc in range(26000,28200):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Textile"
    if cpc in range(31000,32000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Wood, straw & cork"
    if cpc in range(32000,33000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Pulp & paper"
    if cpc in range(33000,34000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(34000,36000):
        acts_all.at[i, "prod_category"] = "Chemical"
        acts_all.at[i, "prod_sub_category"] = "Chemical products"
    if cpc in range(34700,34800):
        acts_all.at[i, "prod_category"] = "PlastRub"
        acts_all.at[i, "prod_sub_category"] = "Plastics & rubber products"
    if cpc in range(35500,37000):
        acts_all.at[i, "prod_category"] = "PlastRub"
        acts_all.at[i, "prod_sub_category"] = "Plastics & rubber products"
    if cpc in range(37000,38000):
        acts_all.at[i, "prod_category"] = "GlasNonMetal"
        acts_all.at[i, "prod_sub_category"] = "Glass and other non-metallic products"
    if cpc in range(39000,40000):
        acts_all.at[i, "prod_category"] = "AgriForeAnim"
        acts_all.at[i, "prod_sub_category"] = "Agricultural and forestry products"
    if cpc in range(40000,42000):
        acts_all.at[i, "prod_category"] = "MetalAlloy"
        acts_all.at[i, "prod_sub_category"] = "Basic metals & alloys, their semi-finished products"
    if cpc in range(42000,43000):
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Food & beverages, animal feed"
    if cpc in range(43000,49000):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Metal/electronic equipments and parts"
    if cpc in range(49000,49400):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Transport vehicles"
    if cpc in range(49000,49915):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Transport vehicles"
    if cpc in range(49941,50000):
        acts_all.at[i, "prod_category"] = "MachElecTrans"
        acts_all.at[i, "prod_sub_category"] = "Metal/electronic equipments and parts"
    if cpc in range(60000,70000):
        acts_all.at[i, "prod_category"] = "OreMinFuel"
        acts_all.at[i, "prod_sub_category"] = "Ores, minerals & fuels"
    if cpc in range(88000,90000):
        acts_all.at[i, "prod_category"] = "MetalAlloy"
        acts_all.at[i, "prod_sub_category"] = "Basic metals & alloys, their semi-finished products"
    if cpc == 38100: #wooden furniture
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Wood, straw & cork"
    if cpc == 38450: #fishing stuff
        acts_all.at[i, "prod_category"] = "ProcBio"
        acts_all.at[i, "prod_sub_category"] = "Textile"



FM_cats = ["OreMinFuel", "Chemical", "PlastRub", "GlasNonMetal", "MetalAlloy", "MachElecTrans"]
acts_FM = acts_all[acts_all.prod_category.isin(FM_cats)]
acts_FM = acts_FM[['name', 'reference product',  "ISIC_name", "ISIC", "CPC_name", "CPC","prod_category", "prod_sub_category", "code", 'activity type']]
acts_FM.rename(columns={"code": "code_EI"}, inplace=True)

substances_FM = acts_FM[acts_FM["activity type"] == "market activity"]
processes_FM = acts_FM[acts_FM["activity type"] == "ordinary transforming activity"]

acts_FM.to_csv('data/activities_from_ei_con319.csv', index=False)
substances_FM.to_csv('data/substances_from_ei_con319.csv', index=False)
processes_FM.to_csv('data/processes_from_ei_con319.csv', index=False)




# isic = [x.split(":") for x in acts_all.ISIC.unique()]
# isic = [x[1] for x in isic if len(x) == 2]
# isic.sort()
# print("\t# of ISIC categories:", len(isic))
# cpc =  acts_all.CPC.unique().tolist()
# cpc.sort()
# print("\t# of CPC categories:", len(cpc))


