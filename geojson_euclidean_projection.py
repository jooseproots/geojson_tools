# pip install matplotlib shapely pyproj geojson
import json

import matplotlib.pyplot
import shapely
import pyproj
import geojson

    
class GeoJSONProjector:
    def __init__(self, geodata: dict, rotate_deg: int = 0, scale_factor: float = 1.0):
        self.geodata = geodata
        self.source_polygons = self._get_source_polygons()
        self.projected_polygons = None

        self.rotate_deg = rotate_deg
        self.scale_factor = scale_factor

    def _get_source_polygons(self) -> list:
        return [feature for feature in self.geodata["features"] if feature["geometry"]["type"] == "Polygon"]
    
    def set_new_geodata(self, geodata: dict) -> None:
        """Set new GeoJSON data."""
        self.geodata = geodata
        self.source_polygons = self._get_source_polygons()
        self.projected_polygons = None

    def _get_transformation_to_UTM(self):
        # What is UTM? - https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system
        if not self.source_polygons:
            raise ValueError("No polygon features available for transformation")

        # Compute a custom localized UTM projection based on average centroid
        all_centroids = [shapely.geometry.shape(feature["geometry"]).centroid for feature in self.source_polygons]
        average_longitude = sum(c.x for c in all_centroids) / len(all_centroids)

        UTM_based_localized_coordinate_system = pyproj.CRS.from_user_input(
            f'+proj=utm +zone={(int((average_longitude + 180) / 6) + 1)} +datum=WGS84 +units=m +no_defs'
        )
        # Create a transformer from EPSG:4326 to the chosen UTM CRS (Coordinate Reference System).
        raw_transformation_to_UTM = pyproj.Transformer.from_crs("EPSG:4326", UTM_based_localized_coordinate_system, always_xy=True).transform
        lambda_transformation_to_UTM = lambda x, y: raw_transformation_to_UTM(x, y)

        return lambda_transformation_to_UTM
    
    def project_to_UTM(self) -> list:
        if not self.source_polygons:
            raise ValueError("No polygon features available for transformation")
    
        transformation_to_UTM = self._get_transformation_to_UTM()
        projected_polygons = [
            {                               
                "geometry": shapely.transform(
                    transformation=transformation_to_UTM,
                    geometry=shapely.geometry.shape(polygon["geometry"]), 
                    interleaved=False # if set to false, then transformation function will be given separate x and y coordinate arrays
                ),
                "properties": polygon["properties"]
            }
            for polygon in self.source_polygons
        ]
        return projected_polygons
    
    def _get_centroid_coordinates(self, polygons: list) -> tuple:
        # Compute global centroid to center everything
        all_coordinates = [
            coordinates 
            for polygon in polygons 
            for coordinates in polygon["geometry"].exterior.coords
        ]
        x_coordinates, y_coordinates = zip(*all_coordinates)
        center_x = sum(x_coordinates) / len(x_coordinates)
        center_y = sum(y_coordinates) / len(y_coordinates)
        return center_x, center_y
    
    def transform_to_localized_coordinate_system(self, UTM_projected_polygons: list):
        transformed_polygons = []

        center_x, center_y = self._get_centroid_coordinates(UTM_projected_polygons)
        for polygon in UTM_projected_polygons:
            geometry = polygon["geometry"]

            geometry = shapely.affinity.translate(geometry, xoff=-center_x, yoff=-center_y)
            if self.rotate_deg:
                geometry = shapely.affinity.rotate(geometry, self.rotate_deg, origin=(0, 0))
            if self.scale_factor != 1.0:
                geometry = shapely.affinity.scale(geometry, xfact=self.scale_factor, yfact=self.scale_factor, origin=(0, 0))

            transformed_polygons.append(
                {
                    "geometry": geometry,
                    "properties": polygon["properties"]
                }
            )
        
        return transformed_polygons

    def project(self) -> list:
        """Project the GeoJSON polygons to Euclidean space."""
        UTM_projected_polygons = self.project_to_UTM()
        transformed_polygons = self.transform_to_localized_coordinate_system(UTM_projected_polygons)

        self.projected_polygons = transformed_polygons

        # TODO: return success/failure status instead
        return transformed_polygons

    def plot(self, ax=None):
        if self.projected_polygons is None:
            raise ValueError("No projected polygons available. Call project() first.")

        if ax is None:
            fig, ax = matplotlib.pyplot.subplots()

        for polygon in self.projected_polygons:
            geometry = polygon["geometry"]
            name = polygon["properties"].get("Name", "")
            # working with names in format "distr123_plot123" and need only number at the end
            name = name.partition("plot")[2]

            if geometry.geom_type == "Polygon":
                x, y = geometry.exterior.xy
                ax.plot(x, y)
                centroid = geometry.centroid
                if name:
                    ax.annotate(name,
                                xy=(centroid.x, centroid.y),
                                ha="center",
                                va="center",
                                fontsize="x-small",
                                bbox=dict(facecolor="white",
                                          alpha=0.5,
                                          edgecolor="none",
                                          pad=0.3))
                    
            elif geometry.geom_type == "MultiPolygon":
                for part in geometry.geoms:
                    x, y = part.exterior.xy
                    ax.plot(x, y)
                    centroid = part.centroid
                    if name:
                        ax.annotate(name,
                                    xy=(centroid.x, centroid.y),
                                    ha="center",
                                    va="center",
                                    fontsize="x-small",
                                    bbox=dict(facecolor="white",
                                              alpha=0.5,
                                              edgecolor="none",
                                              pad=0.3))

        ax.set_aspect("equal")
        ax.grid(True)
        ax.set_title("Euclidean projection of GeoJSON Polygons, scale in meters")
        matplotlib.pyplot.show()

    def cast_to_geojson(self) -> geojson.FeatureCollection:
        """Convert projected polygons to GeoJSON format."""
        if self.projected_polygons is None:
            raise ValueError("No projected polygons available. Call project() first.")
    
        return geojson.FeatureCollection(
            [
                geojson.Feature(
                    properties=feature["properties"],
                    geometry=shapely.geometry.mapping(feature["geometry"])
                ) for feature in self.projected_polygons
            ]
        )
    
#################
# Example usage #
#################

INPUT_GEODATA_PATH = "district1_plots.geojson"
OUTPUT_FILE_PATH = "sample_output.geojson"

with open(INPUT_GEODATA_PATH) as file:
    geodata = json.load(file)

# Initialize with data
projector = GeoJSONProjector(
    geodata=geodata,
    rotate_deg=0,
    scale_factor=1.0
)

# Project and plot
projected_polygons = projector.project()
projector.plot()

# # Get GeoJSON output
# output_geojson = projector.cast_to_geojson()
# with open(OUTPUT_FILE_PATH, "w") as file:
#     json.dump(output_geojson, file, indent=4)

# # Or initialize empty and set data later
# projector = GeoJSONProjector(rotate_deg=45, scale_factor=1.2)
# projector.set_new_geodata(geodata)
# projector.project()
# projector.plot()