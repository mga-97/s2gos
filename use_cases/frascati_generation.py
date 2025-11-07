#!/usr/bin/env python3
import gen_util
from upath import UPath

from s2gos_generator import create_scene_config
from s2gos_generator.core.config import (
    AbsorptionDatabase,
    MolecularAtmosphereConfig,
    ThermophysicalConfig,
    VegetationPlacementConfig,
    VegetationSpecies,
)


def scene_configuration(
        scene_name:str, 
        lat:float, 
        lon:float, 
        target_size:float, 
        output_dir:str|UPath=None
    ):
    """
    Create the scene confifuration corresponding the PNP scene.
    """

    # Create basic configuration using defaults
    config = create_scene_config(
        scene_name=scene_name,
        center_lat=lat,
        center_lon=lon,
        aoi_size_km=target_size,
        output_dir=UPath("./gen_output") if output_dir is None else output_dir,
        target_resolution_m=10.0,
        description="Frascati city and surroundings",
    )

    # Simple boolean flags and direct field assignment
    config.enable_buffer = True
    config.buffer_size_km = 60.0
    config.buffer_resolution_m = 60.0

    config.enable_background = True
    config.background_elevation = 0.0
    config.background_size_km = 150
    config.background_resolution_m = 200.0

    # Configure multi-species vegetation placement with trees and shrubs
    config.vegetation_placement = VegetationPlacementConfig(
        enabled=True,
        landcover_species_mapping={
            10: [  # Treecover
                VegetationSpecies(
                    name="trees",
                    asset_xml_paths=[
                        "tls_tree_25.xml",
                        "tls_tree_71.xml",
                        "tls_tree_165.xml",
                        "tls_tree_228.xml",
                        "tls_tree_290.xml",
                        "tls_tree_300.xml",
                        "tls_tree_336.xml",
                    ],  # Single asset in list
                    # For multiple variants with uniform distribution:
                    # asset_xml_paths=["tree1.xml", "tree2.xml", "tree3.xml"]
                    # For weighted distribution:
                    # asset_xml_paths={"tree_mature.xml": 5.0, "tree_young.xml": 2.0, "tree_old.xml": 1.0}
                    density_per_hectare=450.0,  # Moderate forest density
                    scale_min=0.8,
                    scale_max=1.4,
                )
            ],
            20: [  # Shrubland
                VegetationSpecies(
                    name="shrubs",
                    asset_xml_paths=["tls_tree_336.xml"],  # Single asset in list
                    density_per_hectare=40.0,
                    scale_min=0.4,
                    scale_max=0.8,
                )
            ],
        },
        density_variation=0.5,
        min_spacing=0.1,
        max_instances_per_pixel=2000,
        spillover_max_distance_m=50.0,
        spillover_compatibility={  # Optional: override global
            30: 0.9,  # High spillover into grassland
            20: 0.5,  # Moderate spillover into shrubland
            60: 0.5,
            100: 0.5,
        },
    )

    # print("Added XML scene to configuration - assets and materials will be loaded automatically")
    molecular_config = MolecularAtmosphereConfig(
        thermoprops=ThermophysicalConfig(identifier="afgl_1986-us_standard"),
        absorption_database=AbsorptionDatabase.GECKO,
        has_absorption=True,
        has_scattering=True,
    )

    config.set_atmosphere_molecular(molecular_config)

    print("Basic configuration created")

    # Validate configuration
    errors = config.validate_configuration()
    if errors:
        print(f"Configuration errors: {errors}")
        return None
    else:
        print("Configuration validation passed")

    return config


if __name__ == "__main__":
    print("S2GOS Generation Demo")
    print()

    scene_name = "frascati"
    target_lat =  41.821
    target_lon =  12.570
    target_size = 20

    config = scene_configuration(
        scene_name, target_lat, target_lon, target_size
    )

    success = gen_util.simple_generation_example(config)
    config.to_json(f"./gen_config/{scene_name}_config.json")

    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo encountered issues")
        print("Check dependencies and data paths")
