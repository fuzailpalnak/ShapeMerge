import os
import datetime
import fiona
from geojson import Feature, FeatureCollection, dump

from collections import OrderedDict

from py_oneliner import one_liner


class Save:
    def __init__(self):
        self.out_folder = os.path.join(
            os.path.join(os.getcwd(), "store"), str(datetime.datetime.now().timestamp())
        )
        os.makedirs(self.out_folder)

    def save(self, merged_collection: OrderedDict):
        raise NotImplementedError


class SaveFiona(Save):
    def __init__(self, geometry_type, crs):
        self._geometry_type = geometry_type
        self._crs = crs
        self._schema = {
            "geometry": self.geometry_type,
            "properties": {"My id": "int", "Neighbour_ids": "str"},
        }
        super().__init__()

    @property
    def geometry_type(self):
        return self._geometry_type

    @property
    def crs(self):
        return self._crs

    @property
    def schema(self):
        return self._schema

    def save(self, merged_collection: OrderedDict):
        out_file = os.path.join(self.out_folder, "merged.shp")

        with fiona.open(
            out_file, "w", crs=self.crs, driver="ESRI Shapefile", schema=self.schema
        ) as output:
            one_liner.one_line(
                tag="Save File Initiated",
                tag_data=f"geometry: {self.geometry_type}, crs: {self.crs}, schema: {self.schema}",
                tag_color="yellow",
                tag_data_color="green",
                to_reset_data=True,
                to_new_line_data=True,
            )
            for i in merged_collection.keys():
                newline = {
                    "geometry": merged_collection[i]["geometry"],
                    "properties": {
                        "My id": int(i),
                        "Neighbour_ids": str(merged_collection[i]["ids"]),
                    },
                }
                output.write(newline)
                output.flush()


class SaveGeoJson(Save):
    def __init__(self):
        super().__init__()

    def save(self, merged_collection: OrderedDict):
        out_file = os.path.join(self.out_folder, "merged.geojson")
        features = list()
        for iterator, i in enumerate(merged_collection.keys()):
            features.append(
                Feature(
                    id=iterator,
                    geometry=merged_collection[i]["geometry"],
                    properties={
                        "My id": int(i),
                        "Neighbour_ids": str(merged_collection[i]["ids"]),
                    },
                )
            )
        feature_collection = FeatureCollection(features)
        with open(out_file, "w") as f:
            dump(feature_collection, f)
