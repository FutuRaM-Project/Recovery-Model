#%%

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

""" acts_all = acts_all[
    (acts_all['location'].apply(lambda x: True if any(i in x for i in ['GLO', 'RoW']) else False))
    & (acts_all['unit'] == 'kilogram')
    ] """
# Filter by CPC codes
acts_all["prod_category"] = ""
acts_all["prod_sub_category"] = ""
for i, j in acts_all.iterrows():

    cpc = acts_all.at[i, "CPC"].split(":")[0]
    if len(cpc) < 5:
        cpc += "0"*(5-len(cpc))
    cpc = int(cpc)
    acts_all.at[i, "CPC"] = cpc
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
        acts_all.at[i, "prod_category"] = "WasteTreatment"
        acts_all.at[i, "prod_sub_category"] = "Waste treatment & disposal"
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

# save csv of every activity in ecoinvent
cols = ['name', 'reference product',  "ISIC_name", "ISIC", "CPC_name", "CPC","prod_category", "prod_sub_category", "code", 'activity type', "location", 'production amount', 'unit']

locs = ['CH', 'RoW', 'SE', 'GLO', 'Europe without Switzerland',
       'RER', 'SI', 'PT', 'GR', 'DE', 'AT', 'CZ', 'FR', 'SK', 'BE','ES',
       'PL', 'IT', 'HU', 'HR', 'NL']

priority = {
    "GLO": 0,
    "RoW": 0,
}


acts = acts_all.copy()
#%% 
acts = acts[cols]
acts = acts[acts.location.isin(locs)]
acts["priority"] = acts.location.map(priority)
acts.priority.fillna(1, inplace=True)
acts = acts.sort_values(by=["priority"], ascending=False)
acts = acts.drop_duplicates(subset=["name"], keep='first', ignore_index=True)

acts.to_csv('data/everything_nodupes_ei_con319.csv', index=False)
#%% 

acts_waste = acts[acts.prod_category == "WasteTreatment"]
acts_waste = acts_waste[acts_waste["production amount"] == -1]
acts_waste = acts_waste[acts_waste["activity type"] == "ordinary transforming activity"]
acts_waste = acts_waste[~acts_waste["name"].str.contains("production")]

units = ['kilogram', 'unit']
acts_waste = acts_waste[acts_waste.unit.isin(units)]
len(acts_waste)

drop_ISIC = ['Sawmilling and planing of wood',
       'Support activities for crop production',
       'Processing and preserving of meat',
       'Manufacture of pulp, paper and paperboard',
       'Manufacture of other chemical products n.e.c.',
       'Extraction of natural gas',
       'Extraction of crude petroleum',
       ]

acts_waste = acts_waste[~acts_waste.ISIC_name.isin(drop_ISIC)]

drop_CPC = [' Sawdust and wood waste and scrap',
       ' Waste and scrap of paper or paperboard',' Wastes from food and tobacco industry',' Worn clothing and other worn textile articles', ' Bagasse',' Cotton waste, except garnetted stock',
        ' Bran and other residues from the working of cereals or legumes; vegetable materials and vegetable waste, veget[…]',
          ' Sewage sludge', ' Pharmaceutical waste', ' Waste of man-made fibres']

acts_waste = acts_waste[~acts_waste.CPC_name.isin(drop_CPC)]

acts_waste.ISIC.unique()
acts_waste.ISIC_name.unique()

acts_waste.CPC.unique()
acts_waste.CPC_name.unique()
acts_waste.to_csv("data/waste_activities_from_ecoinvent.csv", sep=";")
len(acts_waste)


# FM_cats = ["OreMinFuel", "Chemical", "PlastRub", "GlasNonMetal", "MetalAlloy", "MachElecTrans"]
# acts_FM = acts_all[acts_all.prod_category.isin(FM_cats)]
# acts_FM = acts_FM[['name', 'reference product',  "ISIC_name", "ISIC", "CPC_name", "CPC","prod_category", "prod_sub_category", "code", 'activity type']]
#substances_FM = acts_FM[acts_FM["activity type"] == "market activity"]
#processes_FM = acts_FM[acts_FM["activity type"] == "ordinary transforming activity"]

acts_FM = acts_waste.copy()
acts_FM.rename(columns={"code": "code_EI"}, inplace=True)
acts_FM.to_csv('data/waste_processes_from_ei_con319.csv', index=False)

acts_FM

# %%
