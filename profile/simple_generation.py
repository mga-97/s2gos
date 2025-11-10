#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from upath import UPath
from s2gos_generator import create_scene_config
from s2gos_generator.core import SceneGenerationPipeline
from s2gos_generator.core.config import (
    MolecularAtmosphereConfig,
    ThermophysicalConfig,
    AbsorptionDatabase,
    VegetationPlacementConfig,
    VegetationSpecies,
)
import json

from s2gos_utils.coordinates import CoordinateSystem

# target_lat = -46.9097
# target_lon = -72.450
target_lat = -46.611111
target_lon = -72.633056

scene_cs = CoordinateSystem(center_lat=target_lat, center_lon=target_lon)


def scene_configuration(target_size, density, buffer, background):  # use_albedo_texturing=False):
    # Create basic configuration using defaults
    
    # name = "pnp_scene"
    name = "pnp_lake"

    scene_name = ( 
        f"{name}_S{int(target_size)}"
        f"_D{int(density)}"
        f"{'_noBu' if not buffer else ''}"
        f"{'_noBa' if not background else ''}_opt"
    )
    
    config = create_scene_config(
        scene_name= scene_name,
        center_lat=target_lat,
        center_lon=target_lon,
        aoi_size_km=target_size,
        output_dir=UPath("./simple_integration_output"),
        target_resolution_m=10.0,
        description="Scene around PNP",
    )

    # S2 presentation figures
    # config = create_scene_config(
    #     scene_name="pnp_scene",
    #     center_lat=target_lat,
    #     center_lon=target_lon,
    #     aoi_size_km=5.0,
    #     output_dir=UPath("./simple_integration_output"),
    #     target_resolution_m=10.0,
    #     description="Scene around PNP",
    # )

    # config = create_scene_config(
    #     scene_name="la_palma",
    #     center_lat=28.721485,
    #     center_lon=-17.861165,
    #     aoi_size_km=10.0,
    #     output_dir=UPath("./simple_integration_output"),
    #     target_resolution_m=10.0,
    #     description="Scene around La Palma",
    # )

    # config = create_scene_config(
    #     scene_name="frascati",
    #     center_lat=41.821,
    #     center_lon=12.67,
    #     aoi_size_km=20.0,
    #     output_dir=UPath("./simple_integration_output"),
    #     target_resolution_m=10.0,
    #     description="Scene around Patagonia",
    # )

    # config = create_scene_config(
    #     scene_name="gobabeb_scene2",
    #     center_lat=-23.6015417,
    #     center_lon=15.1258696,
    #     aoi_size_km=10.0,
    #     output_dir=UPath("./simple_integration_output"),
    #     target_resolution_m=10.0,
    #     description="Scene around Patagonia",
    # )

    # Simple boolean flags and direct field assignment
    config.enable_buffer = buffer
    config.buffer_size_km = 60.0
    config.buffer_resolution_m = 60.0

    config.enable_background = background
    config.background_elevation = 0.0
    config.background_size_km = 150
    config.background_resolution_m = 200.0

    # config.enable_hamster_albedo(
    #     data_path="/home/gonzalezm/s2gos/s2gos/experimenting/HAMSTER_Gobabeb/DOY196_Gobabeb.nc",
    #     variable_name="albedo",
    #     fallback_on_error=True,
    # )
    # Configure multi-species vegetation placement with trees and shrubs

    config.vegetation_placement = VegetationPlacementConfig(
        enabled = (density > 0.),
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
                    density_per_hectare=density,  # Moderate forest density
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


# @profile
def simple_generation_example(target_size, density, buffer, background):

    """Demonstrate complete S2GOS integration with configuration."""
    print("S2GOS Integration Example")
    print("=" * 60)
    print()

    # Step 1: Create and validate configuration
    print("Step 1: Creating scene configuration...")
    config = scene_configuration(target_size, density, buffer, background)
    if not config:
        return False

    # Display configuration summary
    print("\nConfiguration Summary:")
    print(f"  Scene: {config.scene_name}")
    print(
        f"  Location: {config.location.center_lat:.4f}°, {config.location.center_lon:.4f}°"
    )
    print(f"  AOI: {config.location.aoi_size_km} km²")
    print(f"  Resolution: {config.processing.target_resolution_m} m")
    # print(
    #     f"  Buffer: {config.buffer.buffer_size_km} km at {config.buffer.buffer_resolution_m} m resolution"
    # )
    # print(f"  Background: at {config.buffer.background_elevation} m")

    config.to_json(UPath("./scene_gen_config.json"))
    print("  Saved: scene_gen_config.json")

    print("\nStep 2: Generating scene with configuration...")

    try:
        # config.processing.flatten_dem = True
        config.to_json("scene_gen_config.json")

        pipeline = SceneGenerationPipeline(config)

        # Generate DAG visualization
        print("\nGenerating DAG visualization...")
        dag_path = pipeline.visualize_dag()
        if dag_path:
            print(f"DAG saved to: {dag_path}")

        # Print execution schedule
        print("\nResource execution order:")
        dependencies = pipeline.get_resource_dependencies()
        for resource_id, deps in dependencies.items():
            print(f"  {resource_id} (depends on: {deps or 'none'})")

        scene_description = pipeline.run_full_pipeline()

        print("Scene generated successfully!")
        print(f" Location: {config.location.center_lat}, {config.location.center_lon}")
        print(
            f" Target: {config.location.aoi_size_km}km² at {config.processing.target_resolution_m}m"
        )
        if config.has_buffer:
            print(
                f"  Buffer: {config.buffer_size_km}km at {config.buffer_resolution_m}m"
            )
        if config.has_background:
            print(
                f"  Background: {config.background_size_km}km at {config.background_resolution_m}m"
            )
        print(f"  Output: {config.scene_output_dir}")

    except Exception as e:
        print(f"Scene generation failed: {e}")
        scene_description = None

   

    # Summary
    print("\n" + "=" * 60)
    print("Integration Example Complete!")
    print(f"Output directory: {config.scene_output_dir}")

    return True


if __name__ == "__main__":
    import argparse
    # Define the parser
    parser = argparse.ArgumentParser(description='Simulator parser')

    # Declare an argument (`--algo`), saying that the 
    # corresponding value should be stored in the `algo` 
    # field, and using a default value if the argument 
    # isn't given
    parser.add_argument('--size', action="store", dest='size', default=10)
    parser.add_argument('--density', action="store", dest='density', default=450)
    parser.add_argument('--buffer', action="store", dest='buffer', default=True)
    parser.add_argument('--background', action="store", dest='background', default=True)

    # Now, parse the command line arguments and store the 
    # values in the `args` variable
    args = parser.parse_args()

    print("S2GOS Generation Demo")
    print()
    print(f"Parsed density: {args.density}, type: {type(args.density)}")
    print(f"Parsed target size: {args.size}, type: {type(args.size)}")
    print(f"Parsed buffer: {int(args.buffer)}, type: {type(args.buffer)}")
    print(f"Parsed background: {int(args.background)}, type: {type(args.background)}")


    success = simple_generation_example(float(args.size), float(args.density), int(args.buffer), int(args.background))

    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo encountered issues")
        print("Check dependencies and data paths")
