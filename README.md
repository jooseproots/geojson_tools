# geojson_tools

A Python toolkit for anonymizing GeoJSON data, using coordinate localization and Euclidean projections.

## Features

- **GeoJSON Coordinate Localizer**: Transform GeoJSON coordinates to a local coordinate system and back
- **GeoJSON Euclidean Projector**: Project geographic coordinates to UTM with custom localized coordinate reference system for Euclidean measurements and visualization

[What is UTM?](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system)

## Requirements

Install dependencies from requirements.txt:
```bash
pip install -r requirements.txt
```

Or install packages manually:
```bash
pip install matplotlib shapely pyproj geojson
```

## Usage

### Coordinate Localization

```python
import json
from geojson_coordinate_localizer import GeoJSONLocalizer

INPUT_GEODATA_PATH = "sample_input.geojson"
OUTPUT_FILE_PATH = "sample_output.geojson"

# Example 1: Initialize with data
with open(INPUT_GEODATA_PATH) as file:
    geodata = json.load(file)

localizer = GeoJSONLocalizer(geodata)
anonymized_data = localizer.localize_geojson()

# Example 2: Initialize empty and set data later
localizer = GeoJSONLocalizer()
localizer.set_geodata(geodata)
# or
localizer.set_offset_coords((<lat>, <long>))

# Restore data
restored_data = localizer.restore_geojson(anonymized_data)
```

### Euclidean Projection

```python
import json
from geojson_euclidean_projection import GeoJSONProjector

INPUT_GEODATA_PATH = "sample_input.geojson"
OUTPUT_FILE_PATH = "sample_output.geojson"

with open(INPUT_GEODATA_PATH) as file:
    geodata = json.load(file)

# Initialize with data
projector = GeoJSONProjector(
    geodata=geodata,
    rotate_deg=45,
    scale_factor=1.2
)

# Project and plot
projected_polygons = projector.project()
projector.plot()

# Get GeoJSON format output
output_geojson = projector.cast_to_geojson()
with open(OUTPUT_FILE_PATH, "w") as file:
    json.dump(output_geojson, file, indent=4)

# Or initialize empty and set data later
projector = GeoJSONProjector(rotate_deg=45, scale_factor=1.2)
projector.set_new_geodata(geodata)
projector.project()
projector.plot()
```

## Features in Detail

### Coordinate Localizer
- Transforms GeoJSON coordinates to a local coordinate system
- Preserves geometric relationships while anonymizing actual locations
- Supports both Polygon and MultiPolygon geometries
- Includes functions to restore original coordinates

### Euclidean Projector
- Projects geographic coordinates to UTM (Universal Transverse Mercator)
- Plotted polygons in real metric scale
- Automatically selects appropriate UTM zone based on data
- Supports rotation and scaling of projected geometries
- Includes visualization tools
- Maintains GeoJSON compatibility
- Useful over the coordinate localizer because localized WGS84/EPSG:4326 coordinate system polygons look distorted on different latitudes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
