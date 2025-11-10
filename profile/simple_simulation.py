#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from upath import UPath


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

# @profile
def simple_simulation_example(target_size, density, buffer, background):
    from s2gos_utils.scene import SceneDescription

    """Demonstrate complete S2GOS integration with configuration."""
    print("S2GOS Simulation Example")
    print("=" * 60)
    print()
    
    name = "pnp_scene"
    # name = "pnp_lake"

    scene_name = ( 
        f"{name}_S{int(target_size)}"
        f"_D{int(density)}"
        f"{'_noBu' if not buffer else ''}"
        f"{'_noBa' if not background else ''}"
    )

    scene_description = SceneDescription.load_yaml(f"./simple_output/{scene_name}/{scene_name}.yml")
    scene_output_dir = UPath(f"./simple_output/{scene_name}")

    # Step 3: Configure simulation with enhanced sensors
    print("\nStep 3: Configuring simulation...")

    # Create diverse sensor suite
    sensors = [
        # UAV RGB camera
        UAVSensor(
            id="uav_rgb_camera",
            instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
            viewing=LookAtViewing(
                origin=[-1700, -2000, 1620], target=[2500, 5000, 300], up=[0, 0, 1]
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
        #         # origin=[-1700, -2000, 1620], target=[2500, 5000, 300], up=[0, 0, 1]
        #         origin=[+20000, 20000, 15020], target=[0, 00, 300], up=[0, 0, 1]
        #         # origin=[+5000, 5000, 15020], target=[5000, 5000, 0], up=[0, 1, 0]
        #     ),
        #     srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
        #     # srf="sentinel_2a-msi-2",
        #     fov=50.0,
        #     resolution=[1920, 1080],
        #     samples_per_pixel=64,
        # ),

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

    # Generate schema for referenceg``
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
                scene_output_dir,
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
    print(f"Output directory: {scene_output_dir}")

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

    # Individual arguments can be accessed as attributes...
    print("S2GOS Simulation Demo")
    print()
    print(f"Parsed density: {args.density}")
    print(f"Parsed target size: {args.size}")
    print(f"Parsed buffer: {args.buffer}")
    print(f"Parsed background: {args.background}")

    success = simple_simulation_example(
        float(args.size), 
        float(args.density), 
        int(args.buffer), 
        int(args.background)
    )

    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo encountered issues")
        print("Check dependencies and data paths")
