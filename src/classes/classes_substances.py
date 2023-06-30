import pandas as pd
import json
import periodictable
import re
from collections import defaultdict
from visualisation.create_substance_treemap import create_substance_treemap

class Substance:
    """
    A superclass that represents a substance.
    Attributes:
        - name (str): The name of the substance.
        - EC (str): The EC number of the substance.
        - composition (dict): The composition of the substance.
        - attributes_physchem (dict): A dictionary of physical/chemical attributes of the substance.
        - attributes_economic (dict): A dictionary of economic attributes of the substance.
    """
    def __init__(self, name):
        self.name = name
        self.EC = None
        self.tags = []
        self.composition = {}
        self.composition_expanded = self.expand_composition()
        self.composition_expanded_json = self.composition_expanded_to_json()

        self.attributes_physchem = {
            'Melting Point (°C)': None,
            'Boiling Point (°C)': None,
            'Density (g/cm³)': None,
        }
        self.attributes_economic = {
            'Price': None,  # In EUR per gram
            'Criticality': None,
            'Supply Sources': None,
            'Production Volume': None,
            'Industrial Uses': None,
            'Market Trends': None,
        }

    def to_dict(self):
        substance_dict = {
            'Name': self.name,
            "Tags": self.tags,
            'Physical/Chemical Attributes': self.attributes_physchem,
            'Economic Attributes': self.attributes_economic
        }
        return substance_dict
    
    def get_composition(self):
        return self.composition
    
    def expand_composition(self):
        """
        Expands the composition of the substance to include the composition of its components.
        """
        c_ex = self.composition.copy()
        for c, f in self.composition.items():
            if isinstance(c, Element) : c_ex[c.name] = {'fraction': f}
            if isinstance(c, Substance) and not isinstance(c, Element):
                c_ex[c.name] = {'fraction': f, '-': {}}
                for sub_c, sub_f in c.composition.items():
                    if isinstance(sub_c, Element):
                        c_ex[c.name]['-'][sub_c.name] = {'fraction': sub_f * f}
                    if isinstance(sub_c, Substance) and not isinstance(sub_c, Element):
                        c_ex[c.name]['-'][sub_c.name] = {'fraction': sub_f * f, '-': {}}
                        for sub_sub_c, sub_sub_f in sub_c.composition.items():
                            if isinstance(sub_sub_c, Element):
                                c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name] = {'fraction': sub_sub_f * sub_f * f}
                            if isinstance(sub_sub_c, Substance) and not isinstance(sub_sub_c, Element):
                                c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name] = {'fraction': sub_sub_f * sub_f * f, '-': {}}
                                for sub_sub_sub_c, sub_sub_sub_f in sub_sub_c.composition.items():
                                    if isinstance(sub_sub_sub_c, Element):
                                        c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name]['-'][sub_sub_sub_c.name] = {'fraction': sub_sub_sub_f * sub_sub_f * sub_f}
                                    if isinstance(sub_sub_sub_c, Substance) and not isinstance(sub_sub_sub_c, Element):
                                        c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name]['-'][sub_sub_sub_c.name] = {'fraction': sub_sub_sub_f * sub_sub_f * sub_f, '-': {}}
                                        for sub_sub_sub_sub_c, sub_sub_sub_sub_f in sub_sub_sub_c.composition.items():
                                            if isinstance(sub_sub_sub_sub_c, Element):
                                                c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name]['-'][sub_sub_sub_c.name]['-'][sub_sub_sub_sub_c.name] = {'fraction': sub_sub_sub_sub_f * sub_sub_sub_f * sub_sub_f * sub_f}
                                            if isinstance(sub_sub_sub_sub_c, Substance) and not isinstance(sub_sub_sub_sub_c, Element):
                                                c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name]['-'][sub_sub_sub_c.name]['-'][sub_sub_sub_sub_c.name] = {'fraction': sub_sub_sub_sub_f * sub_sub_sub_f * sub_sub_f * sub_f, '-': {}}
                                                for sub_sub_sub_sub_sub_c, sub_sub_sub_sub_sub_f in sub_sub_sub_sub_c.composition.items():
                                                    if isinstance(sub_sub_sub_sub_sub_c, Element):
                                                        c_ex[c.name]['-'][sub_c.name]['-'][sub_sub_c.name]['-'][sub_sub_sub_c.name]['-'][sub_sub_sub_sub_c.name]['-'][sub_sub_sub_sub_sub_c.name] = {'fraction': sub_sub_sub_sub_sub_f * sub_sub_sub_sub_f * sub_sub_sub_f * sub_sub_f * f}
                                                    if isinstance(sub_sub_sub_sub_sub_c, Substance):
                                                        raise ValueError("Composition of more than 5 nested levels is not supported.")
        
        comp_expanded = {}
        for k, v in c_ex.items():
            if isinstance(k, Substance):
                comp_expanded[k.name] = v
            else:
                comp_expanded[k] = v
                
        self.composition_expanded = comp_expanded
        return comp_expanded 

    def composition_expanded_to_json(self):
        j = json.dumps(self.composition_expanded)
        self.composition_expanded_json = j
        return j        

    def to_series(self):
        substance_dict = self.to_dict()
        series = pd.Series(substance_dict)
        return series
    
    def add_tag(self, tag):
        self.tags.append(tag)
    
    def to_json(self, filename):
        data = self._create_treemap_data()
        with open(filename, 'w') as file:
            json.dump(data, file)
    
    def create_treemap(self):
        data = self.composition_expanded
        name = self.name
        create_substance_treemap(data, name)

class Element(Substance):
    """
    A subclass that represents an element.
    Attributes:
        - symbol (str): The symbol of the element.
        - atomic_number (int): The atomic number of the element.
        - atomic_mass (float): The atomic mass of the element.
    """
    def __init__(self, symbol):
        super().__init__(symbol)
        element = periodictable.elements.symbol(symbol)
        self.symbol = element.symbol
        self.atomic_number = element.number
        self.atomic_mass = element._mass
        self.composition = {self: 1}

    def to_dict(self):
        element_dict = super().to_dict()
        element_dict.update({
            'Symbol': self.symbol,
            'Atomic Number': self.atomic_number,
            'Atomic Mass': self.atomic_mass,
        })
        return element_dict

    def to_series(self):
        element_dict = self.to_dict()
        series = pd.Series(element_dict)
        return series
    
    def add_to_model(self, model):
        model.add_element(self)

class Compound(Substance):
    """
    A subclass that represents a compound.
    Attributes:
        - formula: The chemical formula of the compound.
    """
    def __init__(self, name, formula):
        super().__init__(name)
        self.formula = formula
        self.molecular_weight = self.calculate_molecular_weight()
        self.molar_fractions = self.calculate_molar_fractions()
        self.composition = self.calculate_mass_fractions()
        # self.attributes_physchem.update({ "Molecular Weight (g/mol)" : self.molecular_weight})

    def calculate_molecular_weight(self):
        molecular_weight = 0
        for symbol, count in self.formula.items():
            molecular_weight += periodictable.elements.symbol(symbol)._mass * count
        return molecular_weight
    
    def calculate_molar_fractions(self):
        molar_fractions = {}
        total_count = sum(self.formula.values())
        for symbol, count in self.formula.items():
            molar_fractions[symbol] = count / total_count
        return molar_fractions

    def calculate_mass_fractions(self):
        composition = {}
        for symbol, count in self.formula.items():
            composition[Element(symbol)] = periodictable.elements.symbol(symbol)._mass * count / self.molecular_weight
        return composition


    def to_dict(self):
        compound_dict = super().to_dict()
        compound_dict.update({
            'Formula': self.formula,
            'Composition': self.composition,
            'Molar Fractions': self.molar_fractions,
            'Molecular Weight (g/mol)': self.molecular_weight,

        })
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
    # #     composition = {ele: ele_mass/self.molecular_weight for ele, ele_mass in composition.items()}

    # #     return composition

class Material(Substance):
    """
    A subclass that represents a material made up of multiple composition.
    Attributes:
        - composition (dict): A dict of Component objects : fractions representing the composition of the material.
    """
    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition
        self.check_composition()

    def check_composition(self):
        total = sum(self.composition.values())
        if total != 1:
            raise ValueError(f"Component fractions must add up to 1. Not: {total}")
        return True

    def to_dict(self):
        material_dict = super().to_dict()
        material_dict.update({
            'Composition': self.composition
        })
        return material_dict

    def to_series(self):
        material_dict = self.to_dict()
        series = pd.Series(material_dict)
        return series
    
    def add_to_model(self, model):
        model.add_material(self)

class Component(Substance):
    """
    A subclass that represents a component of a material.
    Attributes:
        - substance (Substance): A Substance object representing the substance of the component.
        - fraction (float): The fraction of the substance in the material.
    """
    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition
        self.check_composition()

# make sure that the composition is valid, i.e. that the fractions sum to 1
    def check_composition(self):
        total = 0
        for fraction in self.composition.values():
            total += fraction
        if total != 1:
            raise ValueError(f"Component fractions must add up to 1. Not: {total}")
        return True

    def to_dict(self):
        component_dict = super().to_dict()
        component_dict.update({
            'Composition': self.composition
        })
        return component_dict

    def to_series(self):
        component_dict = self.to_dict()
        series = pd.Series(component_dict)
        return series
    
    def add_to_model(self, model):
        model.add_component(self)

class Product(Substance):
    """
    A subclass that represents a product made up of multiple composition.
    Attributes:
        - composition (list): A list of Component objects representing the composition of the product.
    """
    def __init__(self, name, composition):
        super().__init__(name)
        self.composition = composition

    def to_dict(self):
        product_dict = super().to_dict()
        product_dict.update({
            'Composition': [component.to_dict() for component in self.composition]
        })
        return product_dict

    def to_series(self):
        product_dict = self.to_dict()
        series = pd.Series(product_dict)
        return series
    
    def add_to_model(self, model):
        model.add_product(self)
