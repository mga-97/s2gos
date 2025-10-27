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
from s2gos_simulator.config import (
    SimulationConfig,
    DirectionalIllumination,
    UAVSensor,
    LookAtViewing,
    UAVInstrumentType,
    SpectralResponse,
)
from s2gos_simulator.backends.eradiate_backend import (
    EradiateBackend,
    ERADIATE_AVAILABLE,
)
import json

from s2gos_utils.coordinates import CoordinateSystem

target_lat = -46.611111
target_lon = -72.633056

scene_cs = CoordinateSystem(center_lat=target_lat, center_lon=target_lon)


def scene_configuration():  # use_albedo_texturing=False):
    # Create basic configuration using defaults
    # config = create_scene_config(
    #     scene_name="pnp_scene",
    #     center_lat=-46.9097,
    #     center_lon=-72.450,
    #     aoi_size_km=10.0,
    #     output_dir=UPath("./simple_integration_output"),
    #     target_resolution_m=10.0,
    #     description="Scene around PNP",
    # )

    # S2 presentation figures
    config = create_scene_config(
        scene_name="pnp_scene",
        center_lat=target_lat,
        center_lon=target_lon,
        aoi_size_km=5.0,
        output_dir=UPath("./simple_integration_output"),
        target_resolution_m=10.0,
        description="Scene around PNP",
    )

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
    # config.enable_buffer = True
    # config.buffer_size_km = 60.0
    # config.buffer_resolution_m = 60.0

    # config.enable_background = True
    # config.background_elevation = 0.0
    # config.background_size_km = 150
    # config.background_resolution_m = 200.0

    # config.enable_hamster_albedo(
    #     data_path="/home/gonzalezm/s2gos/s2gos/experimenting/HAMSTER_Gobabeb/DOY196_Gobabeb.nc",
    #     variable_name="albedo",
    #     fallback_on_error=True,
    # )
    # Configure multi-species vegetation placement with trees and shrubs

    config.vegetation_placement = VegetationPlacementConfig(
        enabled=True,
        landcover_species_mapping={
            10: [  # Treecover
                VegetationSpecies(
                    name="trees",
                    asset_xml_paths=[
                        "tls_tree_25.xml",
                        # "tls_tree_71.xml",
                        # "tls_tree_165.xml",
                        # "tls_tree_228.xml",
                        # "tls_tree_290.xml",
                        # "tls_tree_300.xml",
                        # "tls_tree_336.xml",
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

    # # Add HYPERNETS mast at scene center (using string material reference)
    # mast_asset = UserAssets(
    #     object_id="hypernets_mast",
    #     ply_path=UPath("./HYPERNETS_Mast.ply"),
    #     coordinate=[15.1258696, -23.6015417],  # Scene center coordinates
    #     material="rough_aluminum",  # String reference - measured BSDF aluminum material
    #     elevation_offset=1.5,  # Place on ground surface
    #     face_normals=True,  # Use smooth normals for better rendering
    # )
    # config.user_assets.append(mast_asset)

    # # Add XML scene with elegant config-based approach
    # config.xml_scenes.append(XmlSceneConfig(
    #     xml_path="./experimenting/gobabeb_fence_custom.xml",
    #     base_coordinate=(15.1253501, -23.6011482)
    # ))
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
def simple_integration_example():
    """Demonstrate complete S2GOS integration with configuration."""
    print("S2GOS Integration Example")
    print("=" * 60)
    print()

    # Step 1: Create and validate configuration
    print("Step 1: Creating scene configuration...")
    config = scene_configuration()
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
        config.processing.flatten_dem = True
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

    # Step 3: Configure simulation with enhanced sensors
    print("\nStep 3: Configuring simulation...")

    # Create diverse sensor suite
    sensors = [
        # UAV RGB camera
        UAVSensor(
            id="uav_rgb_camera",
            instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
            viewing=LookAtViewing(
                origin=[-1700, -2000, 620], target=[2500, 5000, 300], up=[0, 0, 1]
            ),
            srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
            # srf="sentinel_2a-msi-2",
            fov=50.0,
            resolution=[1920, 1080],
            samples_per_pixel=8,
        ),
        # UAVSensor(
        #     id="uav_rgb_camera",
        #     instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
        #     viewing=LookAtViewing(
        #         origin=[0, 0, 3700], target=[0, 0, 0], up=[0, 1, 0]
        #     ),
        #     srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
        #     # srf="sentinel_2a-msi-2",
        #     fov=40.0,
        #     resolution=[1920, 1920],
        #     samples_per_pixel=1024,
        # ),
        # UAVSensor(
        #     id="uav_rgb_camera2",
        #     instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
        #     viewing=LookAtViewing(
        #         origin=[0, 0, 55000], target=[0, 0, 0], up=[0, 1, 0]
        #     ),
        #     # srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
        #     srf="sentinel_2a-msi-3",
        #     fov=70.0,
        #     resolution=[1080, 1080],
        #     samples_per_pixel=4,
        # ),
        # UAVSensor(
        #     id="uav_rgb_camera3",
        #     instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
        #     viewing=LookAtViewing(
        #         origin=[0, 0, 55000], target=[0, 0, 0], up=[0, 1, 0]
        #     ),
        #     # srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
        #     srf="sentinel_2a-msi-4",
        #     fov=70.0,
        #     resolution=[1080, 1080],
        #     samples_per_pixel=4,
        # ),
        # Sentinel-2 MSI band sensors
        # SatelliteSensor(
        #     id="sentinel2_msi_b2",
        #     platform="sentinel-2a",
        #     instrument="msi",
        #     band="2",  # Blue band
        #     viewing=AngularViewing(zenith=0.0, azimuth=0.0),
        #     target_center_lat=target_lat,  # Same as scene center
        #     target_center_lon=target_lon,  # Same as scene center
        #     target_size_km=2.5,
        #     film_resolution=(250, 250),
        #     samples_per_pixel=1024,
        # ),
        # SatelliteSensor(
        #     id="sentinel2_msi_b3",
        #     platform="sentinel-2a",
        #     instrument="msi",
        #     band="3",  # Green band
        #     viewing=AngularViewing(zenith=0.0, azimuth=0.0),
        #     target_center_lat=target_lat,  # Same as scene center
        #     target_center_lon=target_lon,  # Same as scene center
        #     target_size_km=2.5,
        #     film_resolution=(250, 250),
        #     samples_per_pixel=1024,
        # ),
        # SatelliteSensor(
        #     id="sentinel2_msi_b4",
        #     platform="sentinel-2a",
        #     instrument="msi",
        #     band="4",  # Red band
        #     viewing=AngularViewing(zenith=0.0, azimuth=0.0),
        #     target_center_lat=target_lat,  # Same as scene center
        #     target_center_lon=target_lon,  # Same as scene center
        #     target_size_km=2.5,
        #     film_resolution=(250, 250),
        #     samples_per_pixel=1024,
        # ),
        # SatelliteSensor(
        #     id="sentinel2_msi_b8",
        #     platform="sentinel-2a",
        #     instrument="msi",
        #     band="8",
        #     viewing=AngularViewing(zenith=0.0, azimuth=0.0),
        #     target_center_lat=target_lat,  # Same as scene center
        #     target_center_lon=target_lon,  # Same as scene center
        #     target_size_km=3.5,
        #     film_resolution=(350, 350),
        #     samples_per_pixel=1024,
        # ),
    ]

    simulation_config = SimulationConfig(
        name="config_simulation",
        description="Simulation using scene configuration with both sensors and radiative quantities",
        # illumination=DirectionalIllumination(zenith=55.0, azimuth=0.5, irradiance_dataset="coddington_2022-1_nm"),
        illumination=DirectionalIllumination.from_date_and_location(
            datetime(2024, 1, 1, 18, 0, 0),
            target_lat,
            target_lon,
            "coddington_2022-1_nm",
        ),
        sensors=sensors,
        # radiative_quantities=radiative_quantities,
        # backend_hints={"eradiate": {"mode": "ckd", "absorption_dataset": "mycena"}},
        backend_hints={"eradiate": {"mode": "mono"}},
    )

    # print("COORDINATE STUFF ")
    # hrdf_target = scene_cs.scene_to_latlon(0, -285)
    # print(hrdf_target)
    # simulation_config.add_hdrf_measurement(
    #     viewing_zenith=0.0,
    #     viewing_azimuth=0.0,
    #     target_lat=hrdf_target[0],
    #     target_lon=hrdf_target[1],
    #     srf="sentinel_2a-msi-2",
    #     samples_per_pixel=1024,
    #     measurement_id="HDRF_B2",
    # )
    # simulation_config.add_hdrf_measurement(
    #     viewing_zenith=0.0,
    #     viewing_azimuth=0.0,
    #     target_lat=hrdf_target[0],
    #     target_lon=hrdf_target[1],
    #     srf="sentinel_2a-msi-3",
    #     samples_per_pixel=1024,
    #     measurement_id="HDRF_B3",
    # )
    # simulation_config.add_hdrf_measurement(
    #     viewing_zenith=0.0,
    #     viewing_azimuth=0.0,
    #     target_lat=hrdf_target[0],
    #     target_lon=hrdf_target[1],
    #     srf="sentinel_2a-msi-4",
    #     samples_per_pixel=1024,
    #     measurement_id="HDRF_B4",
    # )

    print("Simulation configured:")
    print(f"  Sensors: {len(simulation_config.sensors)}")
    for i, sensor in enumerate(simulation_config.sensors):
        platform = sensor.platform_type.value
        instrument = getattr(sensor, "instrument", "N/A")
        if hasattr(instrument, "value"):
            instrument = instrument.value
        print(f"    {i + 1}. {sensor.id} ({platform}/{instrument})")

    print(f"  Radiative quantities: {len(simulation_config.radiative_quantities)}")

    # Save simulation configuration
    simulation_config.to_json(UPath("./simulation_config.json"))
    print("  Saved: simulation_config.json")

    # Generate schema for reference
    schema = SimulationConfig.model_json_schema()
    with open("./simulation_schema.json", "w") as f:
        json.dump(schema, f, indent=2)
    print("  Schema: simulation_schema.json")

    # Step 4: Run simulation (if available)
    if ERADIATE_AVAILABLE and scene_description:
        print("\nStep 4: Validating materials and running simulation...")

        # Handle both SceneDescription objects and raw resource dict
        if hasattr(scene_description, "materials"):
            # SceneDescription object
            print("Using SceneDescription object for validation...")
            available_materials = list(scene_description.materials.keys())
            objects_to_check = scene_description.objects
        elif isinstance(scene_description, dict):
            # Raw resource outputs - try to load scene description from path
            print("Using resource outputs dict - attempting to load scene from file...")
            scene_path = scene_description.get("scene_description")
            if scene_path and Path(scene_path).exists():
                try:
                    import yaml

                    with open(scene_path, "r") as f:
                        scene_data = yaml.safe_load(f)
                    available_materials = list(scene_data.get("materials", {}).keys())
                    objects_to_check = scene_data.get("objects", [])
                    print(f"Loaded scene data from {scene_path}")
                except Exception as e:
                    print(f"Could not load scene data: {e}")
                    print("Skipping material validation...")
                    available_materials = []
                    objects_to_check = []
            else:
                print("Scene file not found, skipping material validation...")
                available_materials = []
                objects_to_check = []
        else:
            print("Unknown scene description format, skipping material validation...")
            available_materials = []
            objects_to_check = []

        if available_materials:
            print(f"Available materials: {available_materials}")

            # Check objects for invalid material references
            material_issues = []
            for i, obj in enumerate(objects_to_check):
                if "material" in obj:
                    mat_ref = obj["material"]
                    if mat_ref not in available_materials:
                        material_issues.append(
                            f"Object {i} ({obj.get('object_id', 'unnamed')}) references unknown material '{mat_ref}'"
                        )

            if material_issues:
                print("⚠️  Material validation found issues:")
                for issue in material_issues:
                    print(f"  - {issue}")
                print(
                    "Note: Material validation issues found, but simulation may still work"
                )
            else:
                print(
                    f"✅ All {len(objects_to_check)} object material references are valid"
                )
        else:
            print("Skipping detailed material validation - using scene file as-is")

        # Prepare scene input for simulator
        if hasattr(scene_description, "materials"):
            # SceneDescription object
            scene_input = scene_description
            print("Using SceneDescription object for simulation")
        elif (
            isinstance(scene_description, dict)
            and "scene_description" in scene_description
        ):
            # Try to load the scene description file path
            scene_path = scene_description["scene_description"]
            print(f"Using scene file path for simulation: {scene_path}")
            try:
                from s2gos_utils.scene import SceneDescription

                scene_input = SceneDescription.load_yaml(scene_path)
                print("Successfully loaded SceneDescription for simulation")
            except Exception as e:
                print(f"Could not load SceneDescription for simulation: {e}")
                print(
                    "Simulation may fail - this is expected due to material definition issues"
                )
                scene_input = scene_path  # Pass path as fallback
        else:
            print("No valid scene description available for simulation")
            scene_input = None

        if scene_input:
            # try:
            simulator = EradiateBackend(simulation_config)
            simulator.run_simulation(
                scene_input,
                config.scene_output_dir,
                plot_image=True,
                id_to_plot="uav_rgb_camera",
            )
            print("Simulation completed successfully!")
            # except Exception as e:
            #     print(f"Simulation failed: {e}")
            #     print(
            #         "This is a known issue with material definitions in the generated scene file"
            #     )
            #     return False
        else:
            print("Skipping simulation - no valid scene description available")
    else:
        print("\nStep 4: Simulation skipped")
        if not ERADIATE_AVAILABLE:
            print("  Eradiate not available")
        if not scene_description:
            print("  Scene generation failed")

    # Summary
    print("\n" + "=" * 60)
    print("Integration Example Complete!")
    print(f"Output directory: {config.scene_output_dir}")

    return True


if __name__ == "__main__":
    print("S2GOS Integration Demo")
    print()

    success = simple_integration_example()

    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo encountered issues")
        print("Check dependencies and data paths")
