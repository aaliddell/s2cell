s2cell
======

.. image:: https://github.com/aaliddell/s2cell/workflows/CI/badge.svg
   :alt: CI Status
   :target: https://github.com/aaliddell/s2cell/actions

.. image:: https://img.shields.io/github/license/aaliddell/s2cell
   :alt: License
   :target: https://github.com/aaliddell/s2cell

.. image:: https://img.shields.io/pypi/v/s2cell
   :alt: PyPI Version
   :target: https://pypi.org/project/s2cell/

Minimal Python `S2 <https://s2geometry.io/>`_
`cell ID <https://s2geometry.io/devguide/s2cell_hierarchy.html>`_, S2Point and lat/lon conversion
library.

This library only does conversion between S2 cell ID/token, S2Point and latitude/longitude and was
written as a method to understand the way the S2 cell system works; hopefully this is useful as a
single-file reference on the process. All steps in the conversion are well commented and written to
be understandable rather than necessarily fast.

The library is checked against a test suite generated from the
`reference C++ implementation <https://github.com/google/s2geometry>`_ to ensure conformity with the
standard.

Should you need more complete S2 functionality or a fast C-based implementation, please consider
using the `Python extension included <https://github.com/google/s2geometry/tree/master/src/python>`_
in the s2gemetry repository or the pure-Python `s2sphere <https://pypi.org/project/s2sphere/>`_
implementation.

Issues and PRs are very welcome to improve the descriptions or correct any misunderstandings of the
S2 cell system. Please note that this library strives to be an easy to read reference rather than
aiming for peak performance (it is in Python after all), so PRs which reduce readability of the
implementation (such as for Python specific speed optimisations) are generally discouraged. However,
if you have optimisations that are applicable to S2 implementations across many langauges and can be
described easily, please do consider making a PR.


Installation
------------

This package can be installed from `PyPI <https://pypi.org/project/s2cell/>`_ with pip or any
other Python package manager:

.. code-block::

   pip install s2cell


Usage
-----

TODO


Useful S2 Links
---------------

- `S2 Geometry <https://s2geometry.io/>`_: The S2 Geometry homepage.
- `S2 Cells <https://s2geometry.io/devguide/s2cell_hierarchy>`_: Reference S2 documentation on the
  S2 cell system.
- `Earth Cube <https://s2geometry.io/resources/earthcube>`_: Description of the face cell mapping
  in the S2 cell system.
- `S2 Cell Statistics <https://s2geometry.io/resources/s2cell_statistics>`_: Details on the sizes of
  S2 cells at each level.
- `google/s2geometry <https://github.com/google/s2geometry>`_: The reference C++ and Python
  implementation.
- `google/s2-geometry-library-java <https://github.com/google/s2-geometry-library-java>`_: The
  reference Java implementation.
- `sidewalklabs/s2sphere <https://github.com/sidewalklabs/s2sphere>`_: A pure-Python S2
  implementation.

If you have another S2 related link that may be useful here, please open an Issue or PR.


License
-------

This project is released under the Apache 2.0 License.
