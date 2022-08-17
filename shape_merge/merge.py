import rtree
import fiona
import geojson

from collections import OrderedDict

from shapely.geometry import shape, mapping
from shapely.ops import cascaded_union

from shape_merge.save import SaveFiona, SaveGeoJson

from py_oneliner import one_liner


class ShapeMerge:
    def __init__(self, bounds_buffer=0, geometry_buffer=0, geometry_type=None):
        """

        :param bounds_buffer: During rtree index creation the bounds of individual geometry are added with buffer of 0,
        This param controls on how big the bounds should grow than the given bounds
        'geometry.bounds.buffer(self.__bounds_buffer)'
        :param geometry_buffer: Add buffer to geometries while checking if they intersect
        'geometry_1.buffer(self.__geometry_buffer).intersects(geometry_2.buffer(self.__geometry_buffer))'
        :param geometry_type: 'Polygon', 'MultiPolygon', 'LineString'

        NOTE - CHOOSING LARGE VALUE OF BUFFER WILL INCREASE THE COMPUTATION OVERHEAD
        """
        self._bounds_buffer = bounds_buffer
        self._geometry_buffer = geometry_buffer

        self._index = rtree.index.Index()

        self._visited = list()
        self._feature_geometry_collection = OrderedDict()

        self._geometry_type = geometry_type
        self._save = None

        self._combined_geometries = OrderedDict()

    @property
    def geometry_type(self):
        return self._geometry_type

    @geometry_type.setter
    def geometry_type(self, value):
        self._geometry_type = value

    def populate_index_by_geojson(self, geo_json_path: str):
        obj = geojson.loads(open(geo_json_path).read())
        if "features" not in obj:
            raise KeyError("Key features is required")
        self._save = SaveGeoJson()

        for feature in obj["features"]:
            self.populate_index_by_feature(feature)

    def populate_index_by_fiona(self, shape_file_path: str):
        obj = fiona.open(shape_file_path)
        if self.geometry_type is None:
            self.geometry_type = obj.schema["geometry"]
        if obj.schema["geometry"] != self.geometry_type:
            raise TypeError(
                "Geometry Type Must Be Same, Required {}, Given {}".format(
                    self.geometry_type, obj.schema["geometry"]
                )
            )
        self._save = SaveFiona(geometry_type=self.geometry_type, crs=obj.crs)

        for feature in obj:
            if feature["geometry"]["type"] != self.geometry_type:
                raise TypeError(
                    "Geometry Type Must Be Same, Required {}, Given {}".format(
                        self.geometry_type, feature["geometry"]["type"]
                    )
                )
            self.populate_index_by_feature(feature)

    def populate_index_by_feature(self, feature: dict):
        """
        for feature in feature_collection:
            self.populate_index_by_feature(feature)

        :param feature: Individual feature on which merging is to be performed, must have "id" and "geometry"
        :return:
        """
        if "id" not in feature.keys() and "geometry" not in feature.keys():
            raise KeyError("Missing Keys, Must have keys 'id' and 'geometry'")
        if (
            "type" not in feature["geometry"]
            and "coordinates" not in feature["geometry"]
        ):
            raise KeyError(
                "Missing Keys, Must have keys 'type' and 'coordinates'in feature['geometry']"
            )
        if self.geometry_type is None:
            self.geometry_type = feature["geometry"]["type"]
        if feature["geometry"]["type"] != self.geometry_type:
            raise TypeError(
                "Geometry Type Must Be Same, Required {}, Given {}".format(
                    self.geometry_type, feature["geometry"]["type"]
                )
            )
        feature_id = int(feature["id"])
        geometry = shape(feature["geometry"])

        if self._bounds_buffer > 0:
            geometry = geometry.buffer(self._bounds_buffer)

        self._index.insert(feature_id, geometry.bounds)
        self._feature_geometry_collection[feature_id] = feature["geometry"]

        one_liner.one_line(
            tag="Index Created for feature_id",
            tag_data=f"{feature_id}",
            tag_color="cyan",
        )
        if self._save is None:
            self._save = SaveGeoJson()

    def _simplify_intersecting_ids(self, potential_neighbour_ids, merged_ids) -> list:
        """
        Remove already explored combination and already visited combination
        if 0 has 2,3,4 as neighbours, then 3 might also have any of the neighbours of 0, so an invert intersection is
        taken, to avoid duplicate computation

        0 -> 1, 3, 4, 5
        3 -> 4, 5, 6, 7, 1, 0
        As 1, 4, 5 their neighbours are already explored while the current_id was 0, so there is no need to perform
        the computation again

        [0, 6, 7] = list(set(potential_neighbour_ids) - set(merged_ids))

        And computation on 0 is done as it is already visited, so again avoid duplicate computation
        [6, 7] = list(set([0, 6, 7]) - set(self.__visited))

        :param potential_neighbour_ids:
        :param merged_ids:
        :return:
        """
        potential_neighbour_ids = list(set(potential_neighbour_ids) - set(merged_ids))
        potential_neighbour_ids = list(
            set(potential_neighbour_ids) - set(self._visited)
        )
        return potential_neighbour_ids

    def _check_for_neighbours(self, geometry) -> list:
        """
        Find neighbours which are in geometry.bounds
        :param geometry: ongoing current geometry, geometry whose neighbour are to be found
        :return: [feature_ids of neighbour who are in geometry.bounds]
        """
        return list(self._index.intersection(geometry.bounds))

    @staticmethod
    def _remove_self_intersection(intersecting_feature_ids, feature_id):
        intersecting_feature_ids.remove(feature_id)
        return intersecting_feature_ids

    @staticmethod
    def _make_self_visit(feature_id, geometry) -> (list, list):
        """
        Marks the ongoing feature as a neighbour
        :param feature_id: feature id of the ongoing feature
        :param geometry: shape(feature["geometry"]) of the ongoing feature
        :return: list(feature_id), list(geometry)
        """
        return [feature_id], [geometry]

    def _is_buffered_neighbour(
        self, potential_neighbour_geometry, current_geometry
    ) -> bool:
        """
        From the collection of neighbours found by Rtree current_geometry.bounds, which of them actually intersects
        with current_geometry
        :param potential_neighbour_geometry: geometry of neighbour found by rtree
        :param current_geometry: ongoing geometry, for which neighbour are to be found
        :return: True if intersects else False
        """
        return potential_neighbour_geometry.buffer(self._geometry_buffer).intersects(
            current_geometry.buffer(self._geometry_buffer)
        )

    @staticmethod
    def _is_neighbour(potential_neighbour_geometry, current_geometry) -> bool:
        """
        From the collection of neighbours found by Rtree current_geometry.bounds, which of them actually intersects
        with current_geometry
        :param potential_neighbour_geometry: geometry of neighbour found by rtree
        :param current_geometry: ongoing geometry, for which neighbour are to be found
        :return: True if intersects else False
        """
        return potential_neighbour_geometry.intersects(current_geometry)

    def _new_neighbours(
        self,
        child_id,
        child_geometry,
        neighbours_to_visit,
        neighbours_geometry,
        neighbour_ids,
    ) -> (list, list, list):
        """
        Find all neighbours which intersects with current_id 'i.e. - ongoing feature'

        :param child_id:
        :param child_geometry:
        :param neighbours_to_visit:
        :param neighbours_geometry:
        :param neighbour_ids:
        :return:
        """

        potential_neighbour_ids = self._remove_self_intersection(
            self._check_for_neighbours(child_geometry), child_id
        )

        potential_neighbour_ids = self._simplify_intersecting_ids(
            potential_neighbour_ids, neighbour_ids
        )
        potential_neighbour_ids = list(
            set(potential_neighbour_ids) - set(self._visited)
        )

        for potential_neighbour_id in potential_neighbour_ids:
            is_neighbour = (
                self._is_neighbour(
                    shape(self._feature_geometry_collection[potential_neighbour_id]),
                    child_geometry,
                )
                if self._geometry_buffer == 0
                else self._is_buffered_neighbour(
                    shape(self._feature_geometry_collection[potential_neighbour_id]),
                    child_geometry,
                )
            )
            if is_neighbour:
                neighbours_to_visit.append(potential_neighbour_id)
                neighbours_geometry.append(
                    shape(self._feature_geometry_collection[potential_neighbour_id])
                )

                neighbour_ids.append(potential_neighbour_id)
        return neighbours_to_visit, neighbours_geometry, neighbour_ids

    def _find_my_neighbour(self, parent_id: int, parent_feature: dict):
        """
        Will Find all the intersecting neighbours with the feature_id and will keep on exploring neighbours associated
        with those intersected neighbours and won't stop until no more neighbours to look up

        :param parent_id: int
        :param parent_feature: dict
        :return:
        """
        if parent_id not in self._visited:

            neighbour_ids = list()
            neighbours_to_visit, neighbours_geometry = self._make_self_visit(
                parent_id, shape(parent_feature)
            )

            while len(neighbours_to_visit) != 0:
                child_id = neighbours_to_visit[0]
                child_geometry = shape(self._feature_geometry_collection[child_id])

                (
                    neighbours_to_visit,
                    neighbours_geometry,
                    neighbour_ids,
                ) = self._new_neighbours(
                    child_id,
                    child_geometry,
                    neighbours_to_visit,
                    neighbours_geometry,
                    neighbour_ids,
                )

                neighbours_to_visit.remove(child_id)
                self._visited.append(child_id)
            self._combined_geometries[parent_id] = {
                "ids": neighbour_ids,
                "geometry": mapping(cascaded_union(neighbours_geometry)),
            }

    def merge_geometries(self) -> OrderedDict:
        for iterator, individual_collection in enumerate(
            self._feature_geometry_collection.items()
        ):
            one_liner.one_line(
                tag="Merging of Geometry In Progress",
                tag_data=f"{str(iterator + 1)} / {str(len(self._feature_geometry_collection))}",
                tag_color="cyan",
                to_reset_data=True,
            )

            self._find_my_neighbour(individual_collection[0], individual_collection[1])

        one_liner.one_line(
            tag="Geometry Count",
            tag_data=f"from {len(self._feature_geometry_collection)} "
            f"to {str(len(self._combined_geometries))}",
            tag_color="cyan",
            to_reset_data=True,
            to_new_line_data=True,
        )

        return self._combined_geometries

    def save_geometries(self):
        if self._save is not None:
            one_liner.one_line(
                tag="Saving InProgress",
                tag_data=f"{self._save.__class__.__name__}",
                tag_color="cyan",
                tag_data_color="red",
                to_reset_data=True,
                to_new_line_data=True,
            )
            self._save.save(self._combined_geometries)
