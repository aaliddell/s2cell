:author: Adam Liddell
:description: Changelog for the s2cell Python library
:keywords: S2, S2 Geometry, s2cell, Python, changes, changelog

Changelog
=========

1.7.2
-----

- Further fixed type hinting to prevent unnecessary compatibility break with Python 3.8


1.7.1
-----

- Fixed type hinting to prevent unnecessary compatibility break with Python 3.8


1.7.0
-----

- Added support for finding neighbors of a cell ID
- Updated useful S2 links in docs
- Updated testing for Python 3.11 and 3.12
- Dropped testing of Python versions 3.7 and 3.8. These versions will likely continue to function
  but are no longer explicitly supported


1.6.0
-----

- Dropped support for Python 3.6
- Fixed ``token_is_valid()`` accepting some invalid tokens


1.5.0
-----

- Moved main source out of ``__init__.py``
- Moved docs hosting to Read the Docs
- Updated docs to improve readability


1.4.0
-----

- Removed dependency on NumPy and improved performance


1.3.0
-----

- Added ``cell_id_to_parent_cell_id()`` and ``token_to_parent_token()``
- Added custom exception types for invalid cell IDs and tokens
- Tidied docs generation


1.2.0
-----

- Added token and cell ID validation functions ``cell_id_is_valid()`` and ``token_is_valid()``
- Added ``token_to_canonical_token()``
- Added S2 Concepts page to docs


1.1.1
-----

- Extracted ``_s2_face_uv_to_xyz()`` to a separate function
- Added documentation
- Updated dependencies
- Removed Python 3.5 support


1.1.0
-----

- Added ``cell_id_to_token()`` and ``token_to_cell_id()``
- Added ``cell_id_to_level()`` and ``token_to_level()``
- Added checks for invalid face bits when decoding a cell ID
- Tidied more of the comments and README
- Compressed the S2 reference test suite files to allow more test points in a similar file size


1.0.0
-----

- Initial release of s2cell
