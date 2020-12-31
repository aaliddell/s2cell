:author: Adam Liddell
:description:
    Useful links for the S2 Geometry ecosystem, including documentation, implementations and links
    to existing users of S2.
:keywords: S2, S2 Geometry, links, concepts, visualisations, implementations, users

Useful S2 Links
===============

Your micro 'Awesome S2' list. If you have another S2 related link that may be useful here, please
`open an Issue <https://github.com/aaliddell/s2cell/issues/new>`__ or PR.


Concepts
--------

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
--------------

Mapping and visualisation tools for S2 cells.

- `Region Coverer <http://s2.sidewalklabs.com/regioncoverer/>`__: Interactive S2 cell covering
  calculator.
- `Planetary View  <http://s2.sidewalklabs.com/planetaryview/>`__: Interactive 3D globe view of the
  S2 cell cube mapping.


Implementations
---------------

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
- `s2geometry-d <https://code.dlang.org/packages/s2geometry-d>`__: A D implementation of S2.


Users
-----

Users of S2 in general, not just of this library.

- `Apache Lucene <https://lucene.apache.org/>`__: Used to implement spatial indexing for Apache
  Solr.
- `Azure Data Explorer <https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/geo-point-to-s2cell-function>`__:
  Used by the ``geo_point_to_s2cell`` function.
- `BigQuery <https://cloud.google.com/bigquery/docs/reference/standard-sql/geography_functions>`__:
  Used to implement the BigQuery geography functions.
- `CockroachDB <https://www.cockroachlabs.com/docs/v20.2/spatial-indexes.html>`__: Used to
  implement the spatial indexing.
- `InfluxDB <https://docs.influxdata.com/influxdb/cloud/query-data/flux/geo/shape-geo-data/#generate-s2-cell-id-tokens>`__:
  Used to implement the `Geo` package.
- `MongoDB <https://docs.mongodb.com/manual/core/2dsphere/>`__: Used to implement the ``2dsphere``
  indexing.
- `S2 Users Mailing List <https://groups.google.com/g/s2geometry-io?pli=1>`__: The Google Groups
  mailing list for S2 users and developers.
