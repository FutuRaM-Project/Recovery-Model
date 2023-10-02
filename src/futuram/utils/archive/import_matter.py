"""
import_matter.py

This module contains functions to import matter from
csv files to a model.

Methods:
    import_matter_bulk(dir_compositions, model)
    import_matter_csv(model, filename)

Dependencies:
    os
    csv
    decimal


"""


import os
import csv
from decimal import Decimal

from ..classes.matter import Element, Compound, Material, Component, Product

matter_types = {
    "element": "elm",
    "compound": "cmp",
    "material": "mat",
    "component": "cpt",
    "product": "prd",
}


def import_matter_bulk(dir_compositions, model):
    """
    Import all composition csvs from the data directory.
    one function scans a directory, and employs the 
    other function in the module to import each csv idividually.

    Csvs should be in a subdirectory called 'compositions-split'
    csvs should have the following naming convention:
    <WS>_<parent_product>_<matter name>-<matter_type>.csv
    where matter types are one of:
    ['elm', 'cmp', 'mat', 'cpt', 'prd']

    Parameters
    ----------
    dir_compositions : str
        The path to the directory containing the csv files.
    
    model : Model

    """
    print(
        f'\n\n{"-" * 30}\n\t Importing matter to {model.name} from {dir_compositions}\n{"-" * 30}'
    )

    # get the list of files in the data directory
    # and extract the matter type store in a tuple
    for v in matter_types.values():
        files = [
            (os.path.join(dir_compositions, x), v)
            for x in os.listdir(dir_compositions)
            if v in x.split("-")[1]
        ]

        # loop over the tuples and import the matter
        for file, matter_type in files:
            # import the matter to the model
            import_matter_csv(model, file)

            matter_name = os.path.basename(file).split("-")[0]
            print(f"Imported {matter_name} as {matter_type} to model {model.name}")


def import_matter_csv(model, filename):
    """
    Import a csv file containing matter data.

    Parameters
    ----------

    model : Model
        The model object to add the matter to.
    
    filename : str
        The path to the csv file.


    The csv should have the structure of the following example:

    filename = ELV_ICE_ferrous-mat.csv
    "
    fraction,matter,mass,mass_fraction,uncertainty
    Pb,element,18.2,0.65,0.1
    H2SO4,compound,7,0.25,0.1
    plastic,material,2.8,0.1,0.1
    "
    the columns of the csv will end up in the
    composition dictionary with the name of the
    fraction as the key to a dictionary of the other columns.

    the matter_type is determined by the end of the filename,
    e.g. 'ferrous-mat.csv' will be imported as a material.

    To split an xlsx file with multiple sheets into multiple csvs, use:
    "utils.split_xlsx_to_csvs.xlsx_to_csvs(filename)"
    The sheet names should be the same structure as the filename above.
    """

    # get the matter name from the filename

    name = os.path.basename(filename).split("-")[0]

    # make a map of matter types to classes
    matter_type_map = {
        "elm": Element,
        "cmp": Compound,
        "mat": Material,
        "cpt": Component,
        "prd": Product,
    }

    # get the matter type from the filename
    matter_type = matter_type_map.get(filename.split("-")[-1].split(".")[0], None)

    # get the composition data from the csv
    comp_dict = {}
    with open(filename, newline="", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["fraction"] != "":
                fraction = row["fraction"]
                mass_fraction = float(row["mass_fraction"])
                matter_kind = row["matter"]
                uncertainty = float(row["uncertainty"])
                comp_dict[fraction] = {
                    "matter_kind": matter_kind,
                    "mass_fraction": mass_fraction,
                    "uncertainty": uncertainty,
                }

    # check if mass fractions add up to 1
    # convert the mass fractions to Decimal objects
    mass_fractions = [
        Decimal(str(comp_dict[fraction]["mass_fraction"])) for fraction in comp_dict
    ]

    # calculate the sum of the mass fractions
    mass_fractions_sum = sum(mass_fractions)

    # check if the sum is equal to 1
    if mass_fractions_sum != Decimal("1"):
        # calculate the mass fraction for the 'undefined' fraction
        undefined_mass_fraction = Decimal("1") - mass_fractions_sum

        # add the 'undefined' fraction to the composition dictionary
        comp_dict["undefined"] = {
            "matter_kind": "unknown",
            "mass_fraction": undefined_mass_fraction,
            "uncertainty": Decimal("0"),
        }

    # finally, add instantiate the matter object and add it to the model
    if matter_type == Element:
        matter = matter_type(name)
    else:
        matter = matter_type(name, comp_dict)
    # matter.add_to_model(model)
    model.add_matter(matter)

    model.get_matter()
