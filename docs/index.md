# S2GOS-APPS

This package contains applications of the S2GOS generator and simulator.

## Installation

You can install the default and development version using:

```bash
# default
pixi install
# dev
pixi install -e dev
```

## Configuration

* The S2GOS package suite can be configured by having a settings file in your current working directory or any parents to it.
* The file should be named "s2gos_settings.yaml"
* Here is a template example:

```yaml
# s2gos_settings.yaml
common:
    search_paths:
        - "./resources/data"
        - "./data"

generator:
    dataset:
        dem:
            name: "Copernicus-DEM-30"
            crs: "EPSG:4326"
            type: indexed-geotiff
            root_directory: "/path/to/dem/tiles"
            index_path: "/path/to/dem_index.feather"
            path_column: "path_dem"
            variable_name: elevation

        landcover:
            name: "ESA Worldcover 2021"
            crs: "EPSG:4326"
            type: zarr
            path:
                value: "s3://bucket/worldcover.zarr"
                cid: "my_s3_creds"
            variable_name: landcover

    files:
        material_config: "./materials.json"
```

* See the [common](s2gos-utils/configuration.md) and [generator](s2gos-generator/configuration.md) configuration pages for additional information.
* Secrets can be provided either through environment variables or a `.secrets.yaml` file. See [the credentials page](../packages/s2gos-utils/docs/credentials.md) for details on how to set this up.
