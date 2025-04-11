# pip install matplotlib, shapely, pyproj, geojson
import json

import matplotlib
import shapely
import pyproj
import geojson

    
class GeoJSONProjector:
    def __init__(self, rotate_deg: int = 0, scale_factor: float = 1.0):
        self.rotate_deg = rotate_deg
        self.scale_factor = scale_factor

    def _get_transformation_to_UTM(self, original_features: list):
        # What is UTM? - https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system

        # Compute a custom localized UTM projection based on average centroid
        all_centroids = [shapely.geometry.shape(feature['geometry']).centroid for feature in original_features]
        average_longitude = sum(c.x for c in all_centroids) / len(all_centroids)

        UTM_based_localized_coordinate_system = pyproj.CRS.from_user_input(
            f'+proj=utm +zone={(int((average_longitude + 180) / 6) + 1)} +datum=WGS84 +units=m +no_defs'
        )
        # Create a transformer from EPSG:4326 to the chosen UTM CRS (Coordinate Reference System).
        raw_transformation_to_UTM = pyproj.Transformer.from_crs("EPSG:4326", UTM_based_localized_coordinate_system, always_xy=True).transform
        lambda_transformation_to_UTM = lambda x, y: raw_transformation_to_UTM(x, y)

        return lambda_transformation_to_UTM

    def project_polygons(self, original_features: list) -> list:
        transformation_to_UTM = self._get_transformation_to_UTM(original_features)
        projected_features = [                                                                                    # if set to false, then transformation function will take separate x and y
            shapely.transform(transformation=transformation_to_UTM, geometry=shapely.geometry.shape(feature['geometry']), interleaved=False)
            for feature in original_features
        ]

        # Compute global centroid to center everything
        all_coordinates = [coordinates for feature in projected_features for coordinates in feature.exterior.coords]
        x_coordinates, y_coordinates = zip(*all_coordinates)
        center_x = sum(x_coordinates) / len(x_coordinates)
        center_y = sum(y_coordinates) / len(y_coordinates)

        transformed_polygons = []
        for feature in projected_features:
            feature = shapely.affinity.translate(feature, xoff=-center_x, yoff=-center_y)
            if self.rotate_deg:
                feature = shapely.affinity.rotate(feature, self.rotate_deg, origin=(0, 0))
            if self.scale_factor != 1.0:
                feature = shapely.affinity.scale(feature, xfact=self.scale_factor, yfact=self.scale_factor, origin=(0, 0))
            transformed_polygons.append(feature)

        return transformed_polygons

    def plot(self, projected_polygons: list, ax=None):
        if ax is None:
            fig, ax = matplotlib.pyplot.subplots()

        for polygon in projected_polygons:
            if polygon.geom_type == "Polygon":
                x, y = polygon.exterior.xy
                ax.plot(x, y)
            elif polygon.geom_type == "MultiPolygon":
                for part in polygon.geoms:
                    x, y = part.exterior.xy
                    ax.plot(x, y)

        ax.set_aspect('equal')
        ax.grid(True)
        ax.set_title("Euclidean projection of GeoJSON Polygons, scale in meters")
        matplotlib.pyplot.show()

    def cast_to_geojson(self, projected_polygons: list) -> geojson.FeatureCollection:
        return geojson.FeatureCollection([
            geojson.Feature(geometry=shapely.geometry.mapping(polygon)) for polygon in projected_polygons
        ])
    
#################
# Example usage #
#################

with open('experiment_plot_restored.geojson') as file:
    geodata = json.load(file)
polygon_features = [feature for feature in geodata['features'] if feature['geometry']['type'] == 'Polygon']

projector = GeoJSONProjector(rotate_deg=0, scale_factor=1.0)
projected_polygons = projector.project_polygons(polygon_features)

# projector.plot(projected_polygons)

# Optionally get the transformed shapes as GeoJSON and write to file
transformed_geojson = projector.cast_to_geojson(projected_polygons)
with open("flattened.geojson", "w") as file:
    json.dump(transformed_geojson, file, indent=4)