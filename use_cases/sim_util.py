import os
from datetime import datetime
from pathlib import Path

import numpy as np
from s2gos_simulator.backends.eradiate_backend import (
    ERADIATE_AVAILABLE,
    EradiateBackend,
)
from s2gos_simulator.config import (
    DirectionalIllumination,
    LookAtViewing,
    SimulationConfig,
    SpectralResponse,
    UAVInstrumentType,
    UAVSensor,
)
from upath import UPath


def top_down_perspective_sensor(target_size, fov, spp):
    distance = (target_size / 2.0) / np.tan(np.deg2rad(fov / 2))

    return UAVSensor(
        id="uav_rgb_camera",
        instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
        viewing=LookAtViewing(
            origin=[0.0, 0.0, distance * 1000], target=[0.0, 0.0, 0.0], up=[0, 1, 0]
        ),
        srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
        fov=fov,
        resolution=[512, 512],
        samples_per_pixel=spp,
    )


def simulation_config(scene_name, target_lat, target_lon, target_size, gmt_hour, spp=8):
    """Demonstrate complete S2GOS simualtion."""
    print("S2GOS Simulation Example")
    print("=" * 60)
    print()

    # Step 3: Configure simulation with enhanced sensors
    print("\nStep 3: Configuring simulation...")

    # create top down sensor
    fov = 50
    sensors = [
        top_down_perspective_sensor(target_size, fov, spp),
    ]

    simulation_config = SimulationConfig(
        name="config_simulation",
        description="Simulation using scene configuration with both sensors and radiative quantities",
        illumination=DirectionalIllumination.from_date_and_location(
            datetime(2024, 1, 1, gmt_hour, 0, 0),
            target_lat,
            target_lon,
            "coddington_2022-1_nm",
        ),
        sensors=sensors,
        backend_hints={"eradiate": {"mode": "mono"}},
    )

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
    if not os.path.exists("./sim_config"):
        os.mkdir("./sim_config")

    simulation_config.to_json(UPath(f"./sim_config/{scene_name}_config.json"))
    print("  Saved: simulation_config.json")
    return simulation_config


def simple_simulation_example(scene_name: str, simulation_config: SimulationConfig):
    from s2gos_utils.scene import SceneDescription

    # Generate schema for referenceg``
    print("  Schema: simulation_schema.json")

    scene_description = SceneDescription.load_yaml(
        f"./gen_output/{scene_name}/{scene_name}.yml"
    )
    simulation_output_dir = UPath(f"./sim_output/{scene_name}")

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
                scene_dir=UPath(f"./gen_output/{scene_name}"),
                output_dir=simulation_output_dir,
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
    print(f"Output directory: {simulation_output_dir}")

    return True
