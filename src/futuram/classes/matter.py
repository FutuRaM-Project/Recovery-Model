"""
matter.py

This module contains classes for representing matter.

Classes:
- Matter: A superclass that represents matter.
- Element: A subclass that represents an element.
- Compound: A subclass that represents a compound.
- Material: A subclass that represents a material made up of multiple composition.
- Component: A subclass that represents a component of a material.
- Product: A subclass that represents a product.

Dependencies:
- periodictable
- pandas
- json
- re
- ../visualisation/make_matter_treemap.py

:noindex:
"""

import re
import json
import pandas as pd
import periodictable

from futuram.visualisation.make_matter_treemap import make_matter_treemap


class Matter:
    """
    A superclass that represents matter.
    Attributes:
        - name (str): The name of the matter.
        - EC (str): The EC number of the matter.
        - composition (dict)(dict): The composition of the matter.
        - attributes_physchem (dict): A dictionary of physical/chemical attributes of the matter.
        - attributes_economic (dict): A dictionary of economic attributes of the matter.

        The nested composition dictionary should be of the following structure:
    {
        name: {matter_type : string
                 mass_fraction : float between 0 and 1
                 uncertainty : float between 0 and 1},
        name: {matter_type : string
                    mass_fraction : float between 0 and 1
                    uncertainty : float between 0 and 1},

    }

    """

    def __init__(self, name):
        self.name = name
        self.EC = None
        self.type = "matter"
        self.tags = []
        self.composition = {}
        self.composition_expanded = self.expand_composition()
        self.composition_expanded_json = self.composition_expanded_to_json()

        self.attributes_physchem = {
            "Melting Point (°C)": None,
            "Boiling Point (°C)": None,
            "Density (g/cm³)": None,
        }
        self.attributes_economic = {
            "Price": None,  # In EUR per gram
            "Criticality": None,
            "Supply Sources": None,
            "Production Volume": None,
            "Industrial Uses": None,
            "Market Trends": None,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def add_to_model(self, model):
        '''
        Adds the matter object to the model object.

        '''
        model.add_matter(self)

    def to_dict(self):
        """
        Makes a dictionary of the matter object.
        With the following structure:
        {
        'Name': str,
        'Tags': list,
        'Physical/chemical attributes': dict,
        'Economic attributes': dict,
        }

        """
        matter_dict = {
            "Name": self.name,
            "Tags": self.tags,
            "Physical/chemical attributes": self.attributes_physchem,
            "Economic attributes": self.attributes_economic,
        }
        return matter_dict

    def expand_composition(self):
        """
        Expands the composition of the matter to include the composition of its components.

        """

        def expand_component(component, fraction):
            if isinstance(component, Element):
                return {component.name: {"fraction": fraction}}
            elif isinstance(component, Matter) and not isinstance(component, Element):
                expanded = {component.name: {"fraction": fraction, "-": {}}}
                for sub_component, sub_fraction in component.composition.items():
                    sub_expanded = expand_component(
                        sub_component, sub_fraction * fraction
                    )
                    for k, v in sub_expanded.items():
                        if k in expanded[component.name]["-"]:
                            expanded[component.name]["-"][k]["fraction"] += v[
                                "fraction"
                            ]
                        else:
                            expanded[component.name]["-"][k] = v
                return expanded
            else:
                raise ValueError("Invalid component type")

        expanded = {}
        for component, fraction in self.composition.items():
            component_expanded = expand_component(component, fraction)
            for k, v in component_expanded.items():
                if k in expanded:
                    expanded[k]["fraction"] += v["fraction"]
                    for sub_k, sub_v in v["-"].items():
                        if sub_k in expanded[k]["-"]:
                            expanded[k]["-"][sub_k]["fraction"] += sub_v["fraction"]
                        else:
                            expanded[k]["-"][sub_k] = sub_v
                else:
                    expanded[k] = v
        self.composition_expanded = expanded
        return expanded

    def composition_expanded_to_json(self):
        """
        Converts the expanded composition to a json string.

        """
        j = json.dumps(self.composition_expanded)
        self.composition_expanded_json = j
        return j

    def to_series(self):
        """
        Converts the matter object dict to a pandas series.

        """
        matter_dict = self.to_dict()
        series = pd.Series(matter_dict)
        return series

    def add_tag(self, tag):
        '''
        Adds a tag to the matter object's tag list.
        
        '''
        self.tags.append(tag)

    # def to_json(self, filename):
    #     data = create_treemap_data()
    #     with open(filename, 'w') as file:
    #         json.dump(data, file)

    def create_treemap(self):
        """
        Creates a treemap of the matter object.

        """
        data = self.composition_expanded
        name = self.name
        make_matter_treemap(data, name)


class Element(Matter):
    """
    A subclass that represents an element.
    Attributes:
        - symbol (str): The symbol of the element.
        - atomic_number (int): The atomic number of the element.
        - atomic_mass (float): The atomic mass of the element.

    """

    def __init__(self, symbol):
        super().__init__(symbol)
        symbol = self.get_symbol(symbol)
        element = periodictable.elements.symbol(symbol)
        self.name = element.symbol
        self.symbol = element.symbol
        self.name_full = element.name
        self.atomic_number = element.number
        self.atomic_mass = element._mass
        self.composition = {self.name: 1}

    def get_symbol(self, symbol):
        """
        Checks if the composition is a dictionary or a \
            string and converts it to a dictionary if necessary.

        """
        if isinstance(symbol, dict):
            for k in symbol.keys():
                self.symbol = k
        else:
            self.symbol = symbol

        return self.symbol

    def to_dict(self):
        """
        Makes a dictionary of the element object.

        """
        element_dict = super().to_dict()
        element_dict.update(
            {
                "Name": self.name_full,
                "Symbol": self.symbol,
                "Atomic Number": self.atomic_number,
                "Atomic Mass": self.atomic_mass,
            }
        )
        return element_dict

    def to_series(self):
        element_dict = self.to_dict()
        series = pd.Series(element_dict)
        return series

    def add_to_model(self, model):
        model.add_element(self)


class Compound(Matter):
    """
    A subclass that represents a compound.
    Attributes:
        - formula: The chemical formula of the compound.

    """

    def __init__(self, name, composition_molecular):
        super().__init__(name)
        self.formula = self.get_formula(composition_molecular)
        self.molecular_weight = self.calculate_molecular_weight()
        self.molar_fractions = self.calculate_molar_fractions()
        self.composition = self.calculate_mass_fractions()

    def print_formula(self):
        '''
        Prints the formula of the compound.
        
        '''

        print(self.formula)

    def get_formula(self, composition_molecular):
        """
        Checks if the composition is a dictionary \
            or a string and converts it to a dictionary if necessary.

        """
        for k, v in composition_molecular.items():
            if isinstance(v, dict):
                self.formula = self.formula_to_dict(k)
            else:
                self.formula = composition_molecular

        return self.formula

    def formula_to_dict(self, formula):
        """
        Converts a chemical formula string to a dictionary of element symbols and counts.
        Args:
            formula (str): The chemical formula string.

        Returns:
            dict: A dictionary of element symbols and counts.

        """
        pattern = r"([A-Z][a-z]*)(\d*)"
        matches = re.findall(pattern, formula)
        elements = {}
        for symbol, count in matches:
            count = int(count) if count else 1
            if symbol in elements:
                elements[symbol] += count
            else:
                elements[symbol] = count
        return elements

    def calculate_molecular_weight(self):
        """
        calculates the molecular weight of the compound

        """
        molecular_weight = 0
        for symbol, count in self.formula.items():
            molecular_weight += periodictable.elements.symbol(symbol)._mass * count
        return molecular_weight

    def calculate_molar_fractions(self):
        """
        calculates the molar fractions of the compound

        Parameters
        ----------
        molecular_weight : float
            molecular weight of the compound

        Returns
        -------
        molar_fractions : dict

        """
        molar_fractions = {}
        total_count = sum(self.formula.values())
        for symbol, count in self.formula.items():
            molar_fractions[symbol] = count / total_count
        return molar_fractions

    def calculate_mass_fractions(self):
        """
        calculates the mass fractions of the compound

        Parameters
        ----------
        molecular_weight : float
            molecular weight of the compound

        Returns
        -------
        composition : dict

        """
        composition = {}
        for symbol, count in self.formula.items():
            composition[symbol] = (
                periodictable.elements.symbol(symbol)._mass
                * count
                / self.molecular_weight
            )
        return composition

    def to_dict(self):
        """
        Makes a dictionary of the compound object.

        """
        compound_dict = super().to_dict()
        compound_dict.update(
            {
                "Formula": self.formula,
                "Composition": self.composition,
                "Molar Fractions": self.molar_fractions,
                "Molecular Weight (g/mol)": self.molecular_weight,
            }
        )
        return compound_dict

    def to_series(self):
        compound_dict = self.to_dict()
        series = pd.Series(compound_dict)
        return series

    def add_to_model(self, model):
        model.add_compound(self)

    # def convert_formula_to_composition(self):
    # #     # Use regular expression to split the formula into element symbols and counts
    # #     elements = re.findall('[A-Z][a-z]?\d*', self.formula)

    # #     # Create a defaultdict to store the composition
    # #     composition = defaultdict(int)
    # #     self.molecular_weight = 0
    # #     ele_mass = 0
    # #     # Iterate over the elements and extract the symbol and count
    # #     coeffs = 0
    # #     for element in elements:
    # #         symbol = re.findall('[A-Z][a-z]?', element)[0]
    # #         count = re.findall('\d+', element)
    # #         count = int(count[0]) if count else 1
    # #         coeffs += count

    # #         ele_mass = Element(symbol).atomic_mass*count
    # #         self.molecular_weight += count*ele_mass
    # #         composition[Element(symbol)] = ele_mass

    # #     # Convert the composition dictionary to Element objects
    # #     composition = {ele: ele_mass/self.molecular_weight for ele,\
    # # ele_mass in composition.items()}

    # #     return composition


class Material(Matter):
    """
    A subclass that represents a material made up of multiple composition.
    Attributes:
        - composition (dict): A dict of Component objects
        - matter_type (str): The type of matter, e.g. 'material'

    """

    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition
        self.matter_type = "material"


class Component(Matter):
    """
    A subclass that represents a component of a material.
    Attributes:
        - matter (matter): A matter object representing the matter of the component.

    """

    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition
        self.matter_type = "component"


class Product(Matter):
    """
    A subclass that represents a product.
    Attributes:
        - composition (): A dictionary of matter objects\
              representing the composition of the product.

    """

    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition
        self.matter_type = "product"
