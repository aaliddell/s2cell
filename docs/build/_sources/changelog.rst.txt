Changelog
=========

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
