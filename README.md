# Shape-Merge

A Python based GIS library for finding and merging all Geometries that intersects with their neighbour.
The library will iterate over all the geometries provided in the form of following [Inputs](Inputs),
and will look for the neighbours which forms an intersection relationship with its *Parent*
*_```the geometry that looks for intersection is reffered as Parent```_*
either through a direct intersection or an intersection link generated via multiple *Child* *_```geometries which have a relationship associated
with its Parent either as a direct neighbour or via mutiple neighbour is reffered to as a Child```_* intersection.



### Inputs

- The Library accepts inputs in three ways
    - *ShapeFile*
            
            shape_merge = ShapeMerge()
            shape_merge.populate_index_by_fiona(r"path_to_shape_file.shp")
        
    - *GeoJSON*
            
            shape_merge = ShapeMerge(geometry_buffer=0, bounds_buffer=0)
            shape_merge.populate_index_by_geojson(r"path_to_geo_json.geojson")

    - *Iteratively* populating the *index*
            
            shape_merge = ShapeMerge()
            for feature in feature_collection:
                shape_merge.populate_index_by_feature(feature)
    
        - The <code>type(feature)</code> must be <code>dict</code> of the following structure
        
                 {'type': 'Feature', 'id': '0', 'properties': "", 'geometry': {'type': 'GeometryType', 'coordinates': list}}
                 
            
### How to run

After Populating the Index, merging is matter of a function call away <code>shape_merge.merge_geometries()</code> will
start the merging process

           
### Output

<code>shape_merge.merge_geometries()</code> will return a collection of merged geometries of 
<code>type(OrderedDict)</code>, which will contain the merged geometries and the ids of the *Children* which
were associated with the *Parent*, The structure of the <code>OrderedDict</code> will be

        OrderedDict([(0, {'ids': [ ], 'geometry': {'type': 'GeometryType', 'coordinates': []}})])
        
For Inputs provided by *Fiona* and *GeoJSON* will store the output in respective file format for visualization

### Parameters

*<code>bounds_buffer</code>* : During rtree index creation the bounds of individual geometry are added with buffer of 0,
        This param controls on how big the original bounds should grow <code>geometry.bounds.buffer(self.__bounds_buffer)</code>, The bounds of the geometry are
        responsible for finding potential intersecting neighbour i.e everything that lies in the bound is considered as a potential neighbour. A large value of bound value will
        increase the computational overhead.

*<code>geometry_buffer</code>*: Add buffer to geometries while checking if they intersect
        <code>geometry_1.buffer(self.__geometry_buffer).intersects(geometry_2.buffer(self.__geometry_buffer))</code>
        
### Geometry Type

- Geometry Type Can either be
    - MultiPolygon
    - Polygon
    - LineString
    - MultiLineString