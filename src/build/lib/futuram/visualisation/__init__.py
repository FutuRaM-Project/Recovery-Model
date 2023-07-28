'''
subpackage: futuram.visualisation

This subpackage contains methods for visualising a model.

Modules:
- make_matter_treemap.py: Make a treemap of the matter in a model.
- make_flowchart.py: Make a flowchart of the model.
- make_network.py: Make a network of the model.

Dependencies:
- plotly
- networkx
- graphviz
- ../classes/model.py
- ../classes/processes.py
- ../classes/matter.py
- ../classes/flows.py

'''


from .make_matter_treemap import make_matter_treemap
from .make_flowchart import make_flowchart
from .make_network import make_network
