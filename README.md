# Shape-Merge

A Python based GIS library for finding and merging all Geometries that intersects with their neighbour.
The library will iterate over all the geometries provided in the form of following [Inputs](#Inputs),
and will look for the neighbours which forms an intersection relationship with its *Parent*
*_```the geometry that looks for intersection is reffered as Parent```_*
either through a direct intersection or an intersection link generated via multiple *Child* *_```geometries which have a relationship associated
with its Parent either as a direct neighbour or via mutiple neighbour is reffered to as a Child```_* intersection.


### Installation

    $ pip install git+https://github.com/cypherics/ShapeMerge.git#egg=ShapeMerge
    
### Requirements
The library uses [Rtree](https://rtree.readthedocs.io/en/latest/) which has a dependency on [libspatialindex](https://libspatialindex.org/), 
I would recommend on resolving the dependency through [conda](https://anaconda.org/conda-forge/libspatialindex)

- LibSpatialIndex For Linux:


    sudo apt-get update -y
    sudo apt-get install -y libspatialindex-dev
    
    
- LibSpatialIndex For Windows:


I m not sure on how to install for windows, here is a [answer](https://gis.stackexchange.com/questions/120527/installing-libspatialindex-on-windows-8)
, which again i m not sure about. I installed on my windows using conda and i would recommend using conda for hassle
free installation

### Inputs

*ShapeFile*
```python
from shape_merge.merge import ShapeMerge
shape_merge = ShapeMerge()
shape_merge.populate_index_by_fiona(r"path_to_shape_file.shp")
```

*GeoJSON*
```python
from shape_merge.merge import ShapeMerge
shape_merge = ShapeMerge()
shape_merge.populate_index_by_geojson(r"path_to_geo_json.geojson")
```
*Iteratively* populate the *index*
```python
from shape_merge.merge import ShapeMerge
shape_merge = ShapeMerge()
for feature in feature_collection:
    shape_merge.populate_index_by_feature(feature)
```

Feature must be of the following structure:


    {'type': 'Feature', 'id': str, 'properties': dict, 'geometry': {'type': 'GeometryType', 'coordinates': list}}
                 
            
### How to run

After Populating the Index, merging is matter of a function call away, execute the following to begin merging:

    
    shape_merge.merge_geometries()

           
### Output

The Output will be a collection, which will contain the merged geometries and the all the ids that were merged together

    merged_geoemrty = OrderedDict([(0, {'ids': [ ], 'geometry': {'type': 'GeometryType', 'coordinates': []}})])
      
 
### Parameters

*_bounds_buffer_* : 

During rtree index creation the bounds of individual geometry are added with buffer of 0, 
This param controls on how big the original bounds should grow.
    
    geometry.bounds.buffer(self.__bounds_buffer)
    
> The bounds of the geometry are responsible for finding potential intersecting neighbour
> i.e everything that lies in the bound is considered as a potential neighbour. A large value of bound value will 
>increase the computational overhead.

*_geometry_buffer_*: 

Add buffer to geometries while checking if they intersect with each other


    geometry_1.buffer(self.__geometry_buffer).intersects(geometry_2.buffer(self.__geometry_buffer))
        
