import json

##########
# Inputs #
##########

INPUT_GEODATA_PATH = "sample_input.geojson"
OUTPUT_FILE_PATH = "sample_output.geojson"

#############
# Functions #
#############

def find_offset_coordinates(geodata: dict) -> tuple[float, float]:
    # Get first coordinate as reference point
    for feature in geodata['features']:
        coords = feature['geometry']['coordinates']
        geom_type = feature['geometry']['type']

        # Find first vertex of first polygon
        if geom_type == 'Polygon':
            return coords[0][0]
        elif geom_type == 'MultiPolygon':
            return coords[0][0][0]
    return None

def localize_coordinates(coords, x_offset: float, y_offset: float) -> list:
    """Recursively transform coordinates to a localized system."""
    if isinstance(coords[0], (float, int)):
        # It's a single coordinate pair [x, y]
        return [coords[0] - x_offset, coords[1] - y_offset]
    else:
        # It's a nested list (e.g., polygon or multipolygon)
        return [localize_coordinates(sub, x_offset, y_offset) for sub in coords]
    
def restore_localized_coordinates(coords: list, x_offset: float, y_offset: float) -> list:
    """Recursively transform coordinates back to original system by adding offset."""
    if isinstance(coords[0], (float, int)):
        # It's a single coordinate pair [x, y]
        return [coords[0] + x_offset, coords[1] + y_offset]
    else:
        # It's a nested list (e.g., polygon or multipolygon)
        return [restore_localized_coordinates(sub, x_offset, y_offset) for sub in coords]

def anonymize_geojson(geodata: dict, offset_coords: tuple[float, float]) -> dict:
    x_offset, y_offset = offset_coords

    # Translate all features
    for feature in geodata['features']:
        current_coordinates = feature['geometry']['coordinates']
        anonymized_coordinates = localize_coordinates(current_coordinates, x_offset, y_offset)
        feature['geometry']['coordinates'] = anonymized_coordinates

    return geodata

def restore_geojson(geodata: dict, offset_coords: tuple[float, float]) -> dict:
    """Restore anonymized GeoJSON to original coordinate system."""
    x_offset, y_offset = offset_coords

    # Translate all features back
    for feature in geodata['features']:
        current_coordinates = feature['geometry']['coordinates']
        restored_coordinates = restore_localized_coordinates(current_coordinates, x_offset, y_offset)
        feature['geometry']['coordinates'] = restored_coordinates

    return geodata

#################
# Example usage #
#################

# # For localizing coordinates:

# with open(INPUT_GEODATA_PATH) as file:
#     geodata = json.load(file)

# offset_coordinates = find_offset_coordinates(geodata)
# anonymized_geodata = anonymize_geojson(geodata, offset_coordinates)

# with open(OUTPUT_FILE_PATH, 'w') as file:
#     json.dump(anonymized_geodata, file, indent=4)


# # For restoring localized coordinates:

# with open(OUTPUT_FILE_PATH) as file:
#     localized_geodata = json.load(file)

# offset_coordinates = (20, 50)
# restored_geodata = restore_geojson(localized_geodata, offset_coordinates)

# with open("experiment_plot_restored.geojson", 'w') as file:
#     json.dump(restored_geodata, file, indent=4)