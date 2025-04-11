import json

#########################
# Functions and classes #
#########################
    
class GeoJSONLocalizer:
    def __init__(self, geodata: dict = None):
        """Initialize the localizer with optional GeoJSON data.
        
        Args:
            geodata (dict, optional): GeoJSON data to process. If provided, offset coordinates
                                    will be automatically calculated from the first feature.
        """
        self.geodata = geodata
        self.offset_coords = self._calculate_offset_coords() if geodata else None

    def _calculate_offset_coords(self) -> tuple[float, float]:
        """Internal method to calculate offset coordinates from the first feature."""
        for feature in self.geodata['features']:
            coords = feature['geometry']['coordinates']
            geom_type = feature['geometry']['type']

            if geom_type == 'Polygon':
                return coords[0][0]
            elif geom_type == 'MultiPolygon':
                return coords[0][0][0]
        return None

    def set_new_geodata(self, geodata: dict) -> None:
        self.geodata = geodata
        self.offset_coords = self._calculate_offset_coords()

    def set_custom_offset_coords(self, offset_coords: tuple[float, float]) -> None:
        self.offset_coords = offset_coords
        
    def _transform_coordinates(self, coords: list, x_offset: float|int, y_offset: float|int, operation: str = 'localize') -> list:
        """Transform coordinates either by localizing (subtracting) or restoring (adding) offset.
        
        Args:
            coords: List of coordinates to transform
            x_offset: X-coordinate offset
            y_offset: Y-coordinate offset
            operation: Either 'localize' or 'restore'
        """
        if isinstance(coords[0], (float, int)):
            # A single coordinate pair [x, y]
            if operation == 'localize':
                return [coords[0] - x_offset, coords[1] - y_offset]
            return [coords[0] + x_offset, coords[1] + y_offset]
        else:
            # A nested list (e.g., polygon or multipolygon)
            return [self._transform_coordinates(subcoords, x_offset, y_offset, operation) for subcoords in coords]
    
    def _transform_polygons(self, geodata: dict, offset_coords: tuple[float|int, float|int], operation: str = 'localize') -> dict:
        """Transform all polygons in the GeoJSON data.
        
        Args:
            geodata: GeoJSON data to transform
            offset_coords: Tuple of (x_offset, y_offset)
            operation: Either 'localize' or 'restore'
        """
        x_offset, y_offset = offset_coords

        for feature in geodata['features']:
            current_coordinates = feature['geometry']['coordinates']
            transformed_coordinates = self._transform_coordinates(
                current_coordinates, x_offset, y_offset, operation
            )
            feature['geometry']['coordinates'] = transformed_coordinates

        return geodata

    def localize_geojson(self) -> dict:
        """Anonymize the stored GeoJSON data using calculated or set offset coordinates."""
        if not self.geodata or not self.offset_coords:
            raise ValueError("GeoJSON data and offset coordinates must be set before anonymizing")
        
        return self._transform_polygons(self.geodata, self.offset_coords, 'localize')

    def restore_geojson(self, anonymized_data: dict) -> dict:
        """Restore anonymized GeoJSON using stored offset coordinates."""
        if not self.offset_coords:
            raise ValueError("Offset coordinates must be set before restoring")
            
        return self._transform_polygons(anonymized_data, self.offset_coords, 'restore')

#################
# Example usage #
#################

# INPUT_GEODATA_PATH = "sample_input.geojson"
# OUTPUT_FILE_PATH = "sample_output.geojson"

# # Example 1: Initialize with data
# with open(INPUT_GEODATA_PATH) as file:
#     geodata = json.load(file)

# localizer = GeoJSONLocalizer(geodata)
# anonymized_data = localizer.localize_geojson()

# with open(OUTPUT_FILE_PATH, "w") as file:
#     json.dump(anonymized_data, file, indent=4)


# # Example 2: Initialize empty and set data later
# localizer = GeoJSONLocalizer()
# localizer.set_new_geodata(geodata)
# # or
# localizer.set_custom_offset_coords((<lat>, <lon>))

# # Restore data
# restored_data = localizer.restore_geojson(anonymized_data)

# with open(OUTPUT_FILE_PATH, "w") as file:
#     json.dump(anonymized_data, file, indent=4)