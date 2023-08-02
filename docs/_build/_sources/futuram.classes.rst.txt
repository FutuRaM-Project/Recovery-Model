Classes
========

Description
------------

The futuram.classes subpackage contains the classes used to define the objects in the model.

These classes are:

* :class:`futuram.classes.model.Model` (this is the main class and can contain all the other classes)
* :class:`futuram.classes.processes.Process` (these are inserted to the class 'Model')
* :class:`futuram.classes.flows.Flow` (these are inserted to the class 'Process')
* :class:`futuram.classes.matter.Matter` (these are inserted to the class 'Flow')
* :class:`futuram.classes.parameters.Parameter` (these can be act on all the other classes)

The class 'Matter' is a superclass with the following subclasses:

* :class:`futuram.classes.matter.Product`
* :class:`futuram.classes.matter.Component`
* :class:`futuram.classes.matter.Material`
* :class:`futuram.classes.matter.Compound`
* :class:`futuram.classes.matter.Element`

.. image:: /_static/matter.png
   :width: 800
   :align: center


Details
--------

See the API reference for more information on the modules and their functions.

.. autosummary::
..    :toctree: generated

..    futuram.utils


.. Submodules
.. ----------

.. futuram.classes.flows module
.. ----------------------------

.. .. automodule:: futuram.classes.flows
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. futuram.classes.matter module
.. -----------------------------

.. .. automodule:: futuram.classes.matter
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. futuram.classes.model module
.. ----------------------------

.. .. automodule:: futuram.classes.model
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. futuram.classes.parameters module
.. ---------------------------------

.. .. automodule:: futuram.classes.parameters
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. futuram.classes.processes module
.. --------------------------------

.. .. automodule:: futuram.classes.processes
..    :members:
..    :undoc-members:
..    :show-inheritance:
