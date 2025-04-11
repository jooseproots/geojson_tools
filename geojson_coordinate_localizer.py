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

    def localize_coordinates(self, coords: list, x_offset: float, y_offset: float) -> list:
        """Recursively transform coordinates to a localized system."""
        if isinstance(coords[0], (float, int)):
            # It's a single coordinate pair [x, y]
            return [coords[0] - x_offset, coords[1] - y_offset]
        else:
            # It's a nested list (e.g., polygon or multipolygon)
            return [self.localize_coordinates(sub, x_offset, y_offset) for sub in coords]
        
    def restore_localized_coordinates(self, coords: list, x_offset: float, y_offset: float) -> list:
        """Recursively transform coordinates back to original system by adding offset."""
        if isinstance(coords[0], (float, int)):
            # It's a single coordinate pair [x, y]
            return [coords[0] + x_offset, coords[1] + y_offset]
        else:
            # It's a nested list (e.g., polygon or multipolygon)
            return [self.restore_localized_coordinates(sub, x_offset, y_offset) for sub in coords]

    def anonymize_polygons(self, geodata: dict, offset_coords: tuple[float, float]) -> dict:
        x_offset, y_offset = offset_coords

        # Translate all features
        for feature in geodata['features']:
            current_coordinates = feature['geometry']['coordinates']
            localized_coordinates = self.localize_coordinates(current_coordinates, x_offset, y_offset)
            feature['geometry']['coordinates'] = localized_coordinates

        return geodata
    
    def restore_polygons(self, geodata: dict, offset_coords: tuple[float, float]) -> dict:
        """Restore anonymized GeoJSON to original coordinate system."""
        x_offset, y_offset = offset_coords

        # Translate all features back
        for feature in geodata['features']:
            current_coordinates = feature['geometry']['coordinates']
            restored_coordinates = self.restore_localized_coordinates(current_coordinates, x_offset, y_offset)
            feature['geometry']['coordinates'] = restored_coordinates

        return geodata

    def localize_geojson(self) -> dict:
        """Anonymize the stored GeoJSON data using calculated or set offset coordinates."""
        if not self.geodata or not self.offset_coords:
            raise ValueError("GeoJSON data and offset coordinates must be set before anonymizing")
        
        return self.anonymize_polygons(self.geodata, self.offset_coords)

    def restore_geojson(self, anonymized_data: dict) -> dict:
        """Restore anonymized GeoJSON using stored offset coordinates."""
        if not self.offset_coords:
            raise ValueError("Offset coordinates must be set before restoring")
            
        return self.restore_polygons(anonymized_data, self.offset_coords)

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

# # Example 2: Initialize empty and set data later
# localizer = GeoJSONLocalizer()
# localizer.set_geodata(geodata)
# # or
# localizer.set_offset_coords((<lat>, <long>))

# # Restore data
# restored_data = localizer.restore_geojson(anonymized_data)