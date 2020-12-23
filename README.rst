.. image:: https://docs.s2cell.aliddell.com/_static/logo-200.png
   :alt: s2cell logo

s2cell
======

Minimal Python `S2 <https://s2geometry.io/>`__
`cell ID <https://s2geometry.io/devguide/s2cell_hierarchy.html>`__, S2 token and lat/lon conversion
library.

`Docs <https://docs.s2cell.aliddell.com>`__ | `PyPI <https://pypi.org/project/s2cell>`__ | `GitHub <https://github.com/aaliddell/s2cell>`__


.. image:: https://github.com/aaliddell/s2cell/workflows/CI/badge.svg
   :alt: CI Status
   :target: https://github.com/aaliddell/s2cell/actions

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

Should you need more complete S2 functionality or a fast C-based implementation, please consider
using the `Python extension included
<https://github.com/google/s2geometry/tree/master/src/python>`__ in the s2geometry repository or the
pure-Python `s2sphere <https://pypi.org/project/s2sphere/>`__ implementation.

Issues and PRs are very welcome to improve the implementation, descriptions or to correct any
misunderstandings of the S2 cell system. Please note that this library strives to be an easy to read
reference rather than aiming for peak performance (it is in Python after all), so PRs which reduce
readability of the implementation (such as for Python specific speed optimisations) are generally
discouraged. However, if you have optimisations that are applicable to S2 implementations across
many langauges and can be described easily, please do consider making a PR.


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

The lat/lon returned will be the centre of the cell at the level available in the provided cell ID
or token.

There are also a few other useful functions for inspecting or converting a cell ID/token:

.. code-block:: python3

   # Conversion
   s2cell.cell_id_to_token(3383781119341101056)  # -> '2ef59b'
   s2cell.token_to_cell_id('3')                  # -> 3458764513820540928

   # Level extraction
   s2cell.cell_id_to_level(3383781119341101056)  # -> 10
   s2cell.token_to_level('3')                    # -> 0


Useful S2 Links
---------------

Your micro 'Awesome S2' list. If you have another S2 related link that may be useful here, please
`open an Issue <https://github.com/aaliddell/s2cell/issues/new>`__ or PR.


Concepts
********

Core concepts of S2 and the S2 cell system.

- `S2 Geometry <https://s2geometry.io/>`__: The S2 Geometry homepage.
- `S2 Cells <https://s2geometry.io/devguide/s2cell_hierarchy>`__: Reference S2 documentation on the
  S2 cell system.
- `Earth Cube <https://s2geometry.io/resources/earthcube>`__: Description of the face cell mapping
  in the S2 cell system.
- `S2 Cell Statistics <https://s2geometry.io/resources/s2cell_statistics>`__: Details on the sizes
  of S2 cells at each level.
- `Geometry on the Sphere <https://docs.google.com/presentation/d/1Hl4KapfAENAOf4gv-pSngKwvS_jwNVHRPZTTDzXXn6Q/view>`__:
  Presentation on the core concepts of the S2 cell hierarchy.


Visualisations
**************

Mapping and visualisation tools for S2 cells.

- `Region Coverer <http://s2.sidewalklabs.com/regioncoverer/>`__: Interactive S2 cell covering
  calculator.
- `Planetary View  <http://s2.sidewalklabs.com/planetaryview/>`__: Interactive 3D globe view of the
  S2 cell cube mapping.


Implementations
***************

Reference and third-party implementations of S2 in various languages.

- `google/s2geometry <https://github.com/google/s2geometry>`__: The reference C++ and Python
  implementation.
- `google/s2-geometry-library-java <https://github.com/google/s2-geometry-library-java>`__: The
  reference Java implementation.
- `sidewalklabs/s2sphere <https://github.com/sidewalklabs/s2sphere>`__: A pure-Python S2
  implementation.
- `golang/geo <https://github.com/golang/geo>`__: A Go implementation of S2.
- `radarlabs/s2 <https://github.com/radarlabs/s2>`__: NodeJS, Javascript and TypeScript bindings for
  the reference C++ implementation.
- `mapbox/node-s2 <https://github.com/mapbox/node-s2>`__: NodeJS/Javascript bindings for the
  reference C++ implementation.
- `r-spatial/s2 <https://github.com/r-spatial/s2/>`__: R bindings for the reference implementation.


Users
*****

Users of S2 in general, not just of this library.

- `Apache Lucene <https://lucene.apache.org/>`__: Used to implement spatial indexing for Apache
  Solr.
- `BigQuery <https://cloud.google.com/bigquery/docs/reference/standard-sql/geography_functions>`__:
  Used to implement the BigQuery geography functions.
- `MongoDB <https://docs.mongodb.com/manual/core/2dsphere/>`__: Used to implement the ``2dsphere``
  indexing.


License
-------

This project is released under the same license as the reference C++ S2 Geometry implementation,
namely the Apache 2.0 License.
