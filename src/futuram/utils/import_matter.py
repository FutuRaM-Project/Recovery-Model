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
import openpyxl
import pandas as pd
from decimal import Decimal
import re

from futuram.classes.matter import Element, Compound, Material, Component, Product

from futuram.utils.config import CODELIST_MATTER, WS_names

matter_types = {
    "element": "elm",
    "compound": "cmp",
    "material": "mat",
    "component": "cpt",
    "product": "prd",
}


def split_formula(formula):
    # Define a regular expression pattern to match elements and their counts
    pattern = r"([A-Z][a-z]*)(\d*)"
    # Find all matches of the pattern in the formula
    matches = re.findall(pattern, formula)
    # Create a dictionary that maps each element to its count
    elements = {}
    for match in matches:
        element, count = match
        count = int(count) if count else 1
        if element in elements:
            elements[element] += count
        else:
            elements[element] = count
    return elements


def import_matter_codelist(model, CODELIST_MATTER):
    """"""
    path = CODELIST_MATTER

    print(
        f'\n\n{"-" * 60}\n   Importing matter codelist to model "{model.name}" \
        \n   from {path}\n{"-" * 60}\n'
    )

    sheet_names = workbook.sheetnames
    sheet_names = [
        sheet.replace("EEE", "WEEE").replace("VEHICLE", "ELV") for sheet in sheet_names
    ]
    levels_keys = ["Key", "SubKey", "SubSubKey"]
    sheets_WSkeys = [WS_name + key for WS_name in WS_names for key in levels_keys]

    sheets_products = [
        sheet.replace("WEEE", "EEE").replace("ELV", "VEHICLE")
        for sheet in sheet_names
        if sheet in sheets_WSkeys
    ]

    sheets_matter = {
        "element": ["element"],
        "compound": ["compounds"],
        "minerals": ["minerals"],
        "material": ["materialKeyLevel4"],
        "component": ["componentKeyLevel2"],
        "product": sheets_products,
    }

    # not a very fast way to do this (loading the file each time), but simple.
    dict_matter = {}
    for matter_type, sheets in sheets_matter.items():
        for sheet in sheets:
            try:
                df = pd.read_excel(path, sheet_name=sheet)
                df["matter_type"] = f"{matter_type}-{sheet}"
                if matter_type in dict_matter:
                    dict_matter[matter_type] = pd.concat([dict_matter[matter_type], df])
                else:
                    dict_matter[matter_type] = df
            except ValueError as e:
                print(e)

    args = {
        "element": None,
        "compound": split_formula(row["code"]),
        "material": None,
        "component": None,
        "product": None,
    }

    count = 0
    error_count = 0
    for matter_object in Element, Compound, Material, Component, Product:
        matter_type = matter_object.__name__.lower()
        df = dict_matter[matter_type]
        df.columns = [col.lower() for col in df.columns]

        for index, row in df.iterrows():
            try:
                matter = matter_object(row["code"], args[matter_type])
                matter.description = row["description"]
                #! need to add the other columns
                # print(f"Added {matter_type}: \t{matter.name}")
                model.add_matter(matter)
                count += 1
            except Exception as e:
                print(
                    f"\n *********** IMPORT ERROR *********** \n \
                    {e} \n with row: \n {row} \n"
                )
                error_count += 1

    print(
        f"Imported {count} matter objects to model {model.name} with {error_count} errors"
    )


## BELOW IS FROM THE OLD IMPORT_MATTER.PY FILE NEEDS TO BE UPDATED FOR COMPOSITIONS


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
    with open(filename, newline="", encoding="utf-8") as csvfile:
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
