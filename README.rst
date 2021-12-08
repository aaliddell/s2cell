.. image:: https://docs.s2cell.aliddell.com/_static/logo.min.svg
   :width: 200
   :height: 200
   :alt: s2cell logo

s2cell
======

Minimal Python `S2 Geometry <https://s2geometry.io/>`__
`cell ID <https://s2geometry.io/devguide/s2cell_hierarchy.html>`__, token and lat/lon conversion
library.

`Docs <https://docs.s2cell.aliddell.com>`__ | `PyPI <https://pypi.org/project/s2cell>`__ | `GitHub <https://github.com/aaliddell/s2cell>`__


.. image:: https://github.com/aaliddell/s2cell/workflows/CI/badge.svg
   :alt: CI Status
   :target: https://github.com/aaliddell/s2cell/actions

.. image:: https://readthedocs.org/projects/s2cell/badge/?version=latest
   :alt: Documentation Status
   :target: https://docs.s2cell.aliddell.com/en/latest

.. image:: https://img.shields.io/github/license/aaliddell/s2cell
   :alt: License
   :target: https://github.com/aaliddell/s2cell

.. image:: https://img.shields.io/pypi/v/s2cell
   :alt: PyPI Version
   :target: https://pypi.org/project/s2cell/


Overview
--------

This library does conversion between S2 cell ID, S2 token and latitude/longitude and was written as
a method to understand the way the S2 cell system works; hopefully this is useful to others as a
single-file reference on the process, where tracing the relevant parts from the reference C++
implementation can be somewhat daunting. All steps in the conversions are well commented and written
to be understandable and functional rather than strictly fast, although little is different from the
reference implementation.

The library is checked against a test suite generated from the
`reference C++ implementation <https://github.com/google/s2geometry>`__ to ensure conformity with the
standard.

Should you need more complete S2 Geometry functionality or a fast C-based implementation, please
consider using the `Python extension included
<https://github.com/google/s2geometry/tree/master/src/python>`__ in the s2geometry repository or the
pure-Python `s2sphere <https://pypi.org/project/s2sphere/>`__ implementation.

Issues and PRs are very welcome to improve the implementation, descriptions or to correct any
misunderstandings of the S2 cell system. Please note that this library strives to be an easy to read
reference rather than aiming for peak performance (it is in Python after all), so PRs which reduce
readability of the implementation (such as for Python specific speed optimisations) are generally
discouraged. However, if you have optimisations that are applicable to S2 implementations across
many languages and can be described easily, please do consider making a PR.


Installation
------------

This package can be installed from `PyPI <https://pypi.org/project/s2cell/>`__ with pip or any
other Python package manager:

.. code-block:: bash

   pip install s2cell


Usage
-----

The full documentation, including the API Reference, is available at
`docs.s2cell.aliddell.com <https://docs.s2cell.aliddell.com>`__. Below is a quick start guide for
the most common uses.

The library is designed to be minimal, predictable and purely functional. Conversion from lat/lon
(in degrees) to a cell ID or token can be done with the following two functions:

.. code-block:: python3

   s2cell.lat_lon_to_cell_id(-10.490091, 105.641318)  # -> 3383782026967071427
   s2cell.lat_lon_to_token(-10.490091, 105.641318)    # -> '2ef59bd352b93ac3'

By default, these conversions will give you a level 30 leaf-cell as output. If you require a lower
precision level, you can specify this:

.. code-block:: python3

   s2cell.lat_lon_to_cell_id(-10.490091, 105.641318, 10)  # -> 3383781119341101056
   s2cell.lat_lon_to_token(-10.490091, 105.641318, 0)     # -> '3'

Conversion from a cell ID or token to lat/lon (in degrees) can be done with the following two
functions:

.. code-block:: python3

   s2cell.cell_id_to_lat_lon(3383781119341101056)  # -> (-10.452552407574101, 105.6412526632361)
   s2cell.token_to_lat_lon('3')                    # -> (0.0, 90.0)

The lat/lon returned will be the center of the cell at the level available in the provided cell ID
or token.

There are also a few other useful functions for inspecting or converting a cell ID/token:

.. code-block:: python3

   # Conversion between cell ID and token
   s2cell.cell_id_to_token(3383781119341101056)  # -> '2ef59b'
   s2cell.token_to_cell_id('3')                  # -> 3458764513820540928

.. code-block:: python3

   # Level extraction
   s2cell.cell_id_to_level(3383781119341101056)  # -> 10
   s2cell.token_to_level('3')                    # -> 0

.. code-block:: python3

   # Parent cell calculation
   s2cell.cell_id_to_parent_cell_id(3383781119341101056)     # -> 3383782218852728832
   s2cell.cell_id_to_parent_cell_id(3383781119341101056, 2)  # -> 3386706919782612992

   s2cell.token_to_parent_token('2ef59b')                    # -> '2ef59c'
   s2cell.token_to_parent_token('2ef59b', 2)                 # -> '2f'

.. code-block:: python3

   # Token canonicalisation
   s2cell.token_to_canonical_token('2ef59BD352b90') # -> '2ef59bd352b9'


Useful S2 Geometry Links
------------------------

A list of useful links for S2 related concepts and projects can be found
`here <https://docs.s2cell.aliddell.com/useful_s2_links.html>`__.


License
-------

This project is released under the same license as the reference C++ S2 Geometry implementation,
namely the Apache 2.0 License.
