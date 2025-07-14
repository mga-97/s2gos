#!/usr/bin/env python3
from pathlib import Path
from s2gos_generator.core import SceneGenerationPipeline
from s2gos_generator.core.config import (
    SceneGenConfig, create_scene_config, 
    AtmosphereConfig, AtmosphereType, MolecularAtmosphereConfig, HomogeneousAtmosphereConfig, 
    HeterogeneousAtmosphereConfig, ThermophysicalConfig, ParticleLayerConfig,
    AbsorptionDatabase, AerosolDataset, ExponentialDistribution
)
from s2gos_utils.scene.materials.enums import BackgroundMaterial
from s2gos_utils.io.paths import open_file
from s2gos_simulator.config import (
    SimulationConfig, SatelliteSensor, UAVSensor, GroundSensor,
    DirectionalIllumination, AngularViewing, LookAtViewing, AngularFromOriginViewing,
    SpectralResponse, UAVInstrumentType, GroundInstrumentType, RadiativeQuantityConfig,
    MeasurementType
)
from s2gos_simulator.backends.eradiate_backend import EradiateBackend, ERADIATE_AVAILABLE
import json


def scene_configuration():
    # Create basic configuration using defaults
    # config = create_scene_config(
    #     scene_name="pisa_scene",
    #     center_lat=43.732,
    #     center_lon=10.350,
    #     aoi_size_km=10.0,
    #     output_dir=Path("./simple_integration_output"),
    #     target_resolution_m=30.0,
    #     description="Scene around Pisa"
    # )
    
    # config = create_scene_config(
    #     scene_name="kairouan_scene",
    #     center_lat=35.680,
    #     center_lon=10.200,
    #     aoi_size_km=10.0,
    #     output_dir=Path("./simple_integration_output"),
    #     target_resolution_m=30.0,
    #     description="Scene around Kairouan"
    # )
    
    
    config = create_scene_config(
        scene_name="gobabeb_scene",
        center_lat=-23.6002,
        center_lon=15.11956,
        aoi_size_km=10.0,
        output_dir=Path("./simple_integration_output"),
        target_resolution_m=30.0,
        description="Scene around Gobabeb"
    )
    
    # Enable buffer/background system
    config.enable_buffer_system(
        buffer_size_km=60.0,
        buffer_resolution_m=100.0,
        background_elevation=0.0,
        background_resolution_m=200.0
    )
    
    molecular_config = MolecularAtmosphereConfig(
        thermoprops=ThermophysicalConfig(
            identifier="afgl_1986-us_standard",
        ),
        absorption_database=AbsorptionDatabase.GECKO,
        has_absorption=True,
        has_scattering=True
    )
    
    hazy_layer = ParticleLayerConfig(
        aerosol_dataset=AerosolDataset.SIXSV_CONTINENTAL,
        optical_thickness=0.3,  # High aerosol for hazy conditions
        altitude_bottom=0.0,
        altitude_top=1000.0,
        distribution=ExponentialDistribution(rate=5.0),
        reference_wavelength=550.0,
        has_absorption=True
    )
    
    config.set_atmosphere_heterogeneous(
        molecular_config=molecular_config,
        particle_layers=[hazy_layer]
    )
    
    print("Basic configuration created")
    
    # Validate configuration
    errors = config.validate_configuration()
    if errors:
        print(f"Configuration errors: {errors}")
        return None
    else:
        print("Configuration validation passed")
    
    return config


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
    print(f"\nConfiguration Summary:")
    print(f"  Scene: {config.scene_name}")
    print(f"  Location: {config.location.center_lat:.4f}°, {config.location.center_lon:.4f}°")
    print(f"  AOI: {config.location.aoi_size_km} km²")
    print(f"  Resolution: {config.processing.target_resolution_m} m")
    print(f"  Buffer: {config.buffer.buffer_size_km} km at {config.buffer.buffer_resolution_m} m resolution")
    print(f"  Background: at {config.buffer.background_elevation} m")
    
    config.to_json(Path("./scene_gen_config.json"))
    print(f"  Saved: scene_gen_config.json")
    
    print(f"\nStep 2: Generating scene with configuration...")
    
    try:
        pipeline = SceneGenerationPipeline(config)
        scene_description = pipeline.run_full_pipeline()
        
        print(f"Scene generated successfully!")
        print(f" Location: {config.location.center_lat}, {config.location.center_lon}")
        print(f" Target: {config.location.aoi_size_km}km² at {config.processing.target_resolution_m}m")
        if config.has_buffer:
            print(f"  Buffer: {config.buffer.buffer_size_km}km² at {config.buffer.buffer_resolution_m}m")
        print(f"  Output: {config.scene_output_dir}")
        
    except Exception as e:
        print(f"Scene generation failed: {e}")
        scene_description = None
    
    # Step 3: Configure simulation with enhanced sensors
    print(f"\nStep 3: Configuring simulation...")
    
    # Create diverse sensor suite
    sensors = [
        # UAV RGB camera
        UAVSensor(
            id="uav_rgb_camera",
            instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
            viewing=LookAtViewing(
                origin=[0, 0, 55000],
                target=[0, 0, 0],
                up=[0, 1, 0]
            ),
            srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
            fov=70.0,
            resolution=[1024, 1024],
            samples_per_pixel=32
        ),
        
    #     # Custom satellite sensor
    #     SatelliteSensor(
    #         id="custom_satellite", 
    #         platform="custom",
    #         instrument="custom",
    #         band="red",
    #         viewing=AngularViewing(zenith=15.0, azimuth=45.0, target=[0, 0, 0]),
    #         srf=SpectralResponse(type="delta", wavelengths=[660.0]),
    #         samples_per_pixel=64
    #     ),
        
    #     # Ground-based sensor
    #     GroundSensor(
    #         id="ground_hypstar",
    #         instrument=GroundInstrumentType.HYPSTAR,
    #         viewing=AngularFromOriginViewing(
    #             origin=[0, 0, 2],
    #             zenith=0.0,  # Looking nadir
    #             azimuth=0.0,
    #         ),
    #         srf=SpectralResponse(type="delta", wavelengths=[660.0]),
    #         samples_per_pixel=64
    #     )
    # ]
    
    # radiative_quantities = [
    #     RadiativeQuantityConfig(
    #         quantity=MeasurementType.BRF,
    #         srf=SpectralResponse(type="delta", wavelengths=[440.0, 550.0, 660.0]),
    #         viewing_zenith=0.0,
    #         viewing_azimuth=0.0,
    #         samples_per_pixel=64
    #     )
    ]
    
    simulation_config = SimulationConfig(
        name="config_simulation",
        description="Simulation using scene configuration with both sensors and radiative quantities",
        illumination=DirectionalIllumination(zenith=30.0, azimuth=180.0),
        sensors=sensors,
        # radiative_quantities=radiative_quantities,
        backend_hints={
            "eradiate": {
                "mode": "mono"
            }
        }
    )
    
    print(f"Simulation configured:")
    print(f"  Sensors: {len(simulation_config.sensors)}")
    for i, sensor in enumerate(simulation_config.sensors):
        platform = sensor.platform_type.value
        instrument = getattr(sensor, 'instrument', 'N/A')
        if hasattr(instrument, 'value'):
            instrument = instrument.value
        print(f"    {i+1}. {sensor.id} ({platform}/{instrument})")
    
    print(f"  Radiative quantities: {len(simulation_config.radiative_quantities)}")
    
    # Save simulation configuration
    simulation_config.to_json(Path("./simulation_config.json"))
    print(f"  Saved: simulation_config.json")
    
    # Generate schema for reference
    schema = SimulationConfig.model_json_schema()
    with open_file('./simulation_schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"  Schema: simulation_schema.json")
    
    # Step 4: Run simulation (if available)
    if ERADIATE_AVAILABLE and scene_description:
        print(f"\nStep 4: Running simulation...")
        
        try:
            simulator = EradiateBackend(simulation_config)
            dataset = simulator.run_simulation(
                scene_description, 
                config.scene_output_dir, 
                plot_image=True, 
                id_to_plot="uav_rgb_camera"
            )
            print("Simulation completed successfully!")
            
        except Exception as e:
            print(f"Simulation failed: {e}")
            return False
    else:
        print(f"\nStep 4: Simulation skipped")
        if not ERADIATE_AVAILABLE:
            print("  Eradiate not available")
        if not scene_description:
            print("  Scene generation failed")
    
    # Summary
    print(f"\n" + "=" * 60)
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