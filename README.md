# geojson_tools

A Python toolkit for anonymizing GeoJSON data, using coordinate localization and Euclidean projections.

## Features

- **GeoJSON Coordinate Localizer**: Transform GeoJSON coordinates to a local coordinate system and back
- **GeoJSON Euclidean Projector**: Project geographic coordinates to UTM with custom localized coordinate reference system for Euclidean measurements and visualization

## Requirements

Python packages:
```bash
pip install matplotlib shapely pyproj geojson
```

## Usage

### Coordinate Localization

```python
from geojson_coordinate_localizer import anonymize_geojson, find_offset_coordinates

# Read your GeoJSON file
with open("input.geojson") as file:
    geodata = json.load(file)

# Get offset coordinates and localize
offset_coordinates = find_offset_coordinates(geodata)
anonymized_geodata = anonymize_geojson(geodata, offset_coordinates)
```

### Euclidean Projection

```python
from geojson_euclidean_projection import GeoJSONProjector

# Create projector with optional rotation and scaling
projector = GeoJSONProjector(rotate_deg=0, scale_factor=1.0)

# Project polygons and visualize
projected_polygons = projector.project_polygons(polygon_features)
projector.plot(projected_polygons)

# Export as GeoJSON
transformed_geojson = projector.cast_to_geojson(projected_polygons)
```

## Features in Detail

### Coordinate Localizer
- Transforms GeoJSON coordinates to a local coordinate system
- Preserves geometric relationships while anonymizing actual locations
- Supports both Polygon and MultiPolygon geometries
- Includes functions to restore original coordinates

### Euclidean Projector
- Projects geographic coordinates to UTM (Universal Transverse Mercator)
- Scale in meters
- Automatically selects appropriate UTM zone based on data
- Supports rotation and scaling of projected geometries
- Includes visualization tools
- Maintains GeoJSON compatibility
- Useful because localized regular WGS84 coordinate system polygons look distorted on different latitudes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
