#!/usr/bin/env python3
from pathlib import Path
from s2gos_generator.core import SceneGenerationConfig, SceneGenerationPipeline
from s2gos_simulator.config_v2 import (
    SimulationConfig, SatelliteSensor, UAVSensor, GroundSensor,
    DirectionalIllumination, AngularViewing, LookAtViewing, AngularFromOriginViewing,
    SpectralResponse, UAVInstrumentType, GroundInstrumentType
)
from s2gos_simulator.backends.eradiate_backend_v2 import EradiateBackendV2, ERADIATE_AVAILABLE
import json

# Available background material options:
# Vegetation: "treecover", "shrubland", "grassland", "cropland", "mangroves", "wetland"
# Non-vegetation: "concrete", "baresoil", "snow", "moss", "water"
BACKGROUND_MATERIAL = "water"


def simple_integration_example():
    """Demonstrate clean S2GOS integration: generate scene → run simulation."""
    print("S2GOS Simple Integration Example")
    print("=" * 40)
    print("Clean workflow: Scene Generation → Simulation")
    print()
    
    # Step 1: Generate Scene
    print("Step 1: Generating scene...")
    
    config = SceneGenerationConfig(
        center_lat=43.7102,
        center_lon=7.2620,
        aoi_size_km=10.0,
        
        dem_index_path=Path("/home/gonzalezm/s2gos/s2gos/packages/s2gos-generator/src/s2gos_generator/data/dem_index.feather"),
        dem_root_dir=Path("/media/DATA/DEM"),
        landcover_index_path=Path("/home/gonzalezm/s2gos/s2gos/packages/s2gos-generator/src/s2gos_generator/data/landcover_index.feather"), 
        landcover_root_dir=Path("/home/gonzalezm/Data"),
        
        output_dir=Path("./simple_integration_output"),
        scene_name="simple_integration_scene",
        target_resolution_m=30.0,    
        enable_buffer=True,
        buffer_size_km=60.0,
        buffer_resolution_m=100.0,
        
        background_elevation=0.0,
        background_material=BACKGROUND_MATERIAL,
    )
    
    try:
        pipeline = SceneGenerationPipeline(config)
        scene_config = pipeline.run_full_pipeline()
        
        print(f"Scene generated: {scene_config.name}")
        print(f"Location: {scene_config.metadata.center_lat}, {scene_config.metadata.center_lon}")
        print(f"Target area: {config.aoi_size_km}km x {config.aoi_size_km}km at {config.target_resolution_m}m resolution")
        print(f"Buffer area: {config.buffer_size_km}km x {config.buffer_size_km}km at {config.buffer_resolution_m}m resolution")
        if scene_config.background:
            print(f"  Background: {scene_config.background.get('material', 'N/A')} at {scene_config.background.get('elevation', 'N/A')}m elevation")
        print(f"  Assets: {pipeline.output_dir}")
        
    except Exception as e:
        print(f"Scene generation failed: {e}")
        print("Check data paths and ensure required files are accessible")
        return False
    
    # Step 2: Configure Simulation with Enhanced Sensors
    print("\nStep 2: Configuring simulation with enhanced sensors...")
    
    # Create different sensor types using the new config system
    sensors = [
        # UAV perspective camera with RGB bands
        UAVSensor(
            id="uav_rgb_camera",
            instrument=UAVInstrumentType.PERSPECTIVE_CAMERA,
            position=[0, 0, 10000],  # 100m altitude
            viewing=LookAtViewing(
                origin=[0, 0, 10000],
                target=[0, 0, 0],
                up=[0,1,0]
            ),
            srf=SpectralResponse(
                type="delta",
                wavelengths=[440.0, 550.0, 660.0]
            ),
            fov=70.0,
            resolution=[1024, 1024],
            samples_per_pixel=32
        ),
        
        # SatelliteSensor(
        #     id="satellite_visible", 
        #     platform="sentinel-2a",
        #     instrument="msi",
        #     band="4",
        #     viewing=AngularViewing(
        #         zenith=15.0,
        #         azimuth=45.0,
        #         target=[0, 0, 0]
        #     ),
        #     samples_per_pixel=4
        # ),

        SatelliteSensor(
            id="custom_sat", 
            platform="custom",
            instrument="custom",
            band="custom",
            viewing=AngularViewing(
                zenith=15.0,
                azimuth=45.0,
                target=[0, 0, 0]
            ),
            srf=SpectralResponse(
                type="delta",
                wavelengths=[440.0]
            ),
            samples_per_pixel=4
        ),

        # # Satellite sensor with visible spectrum
        # SatelliteSensor(
        #     id="satellite_visible", 
        #     platform="Sentinel-2A",
        #     instrument="MSI",
        #     band="4",
        #     viewing=AngularViewing(
        #         zenith=15.0,
        #         azimuth=45.0,
        #         target=[0, 0, 0]
        #     ),
        #     samples_per_pixel=4
        # ),
        
        # # Multiple satellite sensors for BRDF measurement
        # SatelliteSensor(
        #     id="satellite_nadir",
        #     platform="Sentinel-2A", 
        #     instrument="MSI",
        #     band="4",
        #     viewing=AngularViewing(zenith=0.0, azimuth=0.0),
        #     samples_per_pixel=16
        # ),
        
        # SatelliteSensor(
        #     id="satellite_oblique_15",
        #     platform="Sentinel-2A",
        #     instrument="MSI", 
        #     band="4",
        #     viewing=AngularViewing(zenith=15.0, azimuth=0.0),
        #     samples_per_pixel=128
        # ),
        
        # SatelliteSensor(
        #     id="satellite_oblique_30",
        #     platform="Sentinel-2A",
        #     instrument="MSI",
        #     band="4", 
        #     viewing=AngularViewing(zenith=30.0, azimuth=0.0),
        #     samples_per_pixel=128
        # ),
        
        # Ground-based HYPSTAR sensor
        GroundSensor(
            id="ground_hypstar",
            instrument=GroundInstrumentType.HYPSTAR,
            viewing=AngularFromOriginViewing(
                zenith=0.0,  # Looking up at nadir
                azimuth=0.0,
                origin=[0, 0, 2]  # Looking at point 100m above
            ),
            srf=SpectralResponse(
                type="delta",
                wavelengths=[440.0]
            ),
            samples_per_pixel=64
        )
    ]
    
    schema = SimulationConfig.model_json_schema()
    
    # Write the schema to the specified output file
    with open('./schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    # Create simulation configuration
    experiment_config = SimulationConfig(
        name="enhanced_sensors_simulation",
        description="Enhanced sensor configuration with UAV, satellite, and ground sensors",
        illumination=DirectionalIllumination(zenith=30.0, azimuth=180.0),
        sensors=sensors
    )

    experiment_config.to_json("./config_test")
    
    print(f"Simulation configured: {experiment_config.name}")
    print(f"Number of sensors: {len(experiment_config.sensors)}")
    for i, sensor in enumerate(experiment_config.sensors):
        platform_type = sensor.platform_type.value
        if hasattr(sensor, 'instrument'):
            instrument = sensor.instrument.value if hasattr(sensor.instrument, 'value') else str(sensor.instrument)
        else:
            instrument = "N/A"
        srf_info = "SpectralResponse" if isinstance(sensor.srf, SpectralResponse) else "string" if isinstance(sensor.srf, str) else "None"
        print(f"  {i+1}. {sensor.id} ({platform_type}/{instrument}) - SRF: {srf_info}")
    
    # Step 3: Run Simulation
    if ERADIATE_AVAILABLE:
        print("\nStep 3: Running Eradiate simulation...")
        
        try:
            simulator = EradiateBackendV2(experiment_config)
            dataset = simulator.run_simulation(scene_config, pipeline.output_dir, plot_image=True, id_to_plot="uav_rgb_camera")
            
            print("Simulation complete!")
                
        except Exception as e:
            print(f"Simulation failed: {e}")
            return False
    else:
        print("\nStep 3: Skipping simulation (Eradiate not available)")
        print("Install Eradiate to run simulations: pip install eradiate[kernel]")
    
    print("\n" + "=" * 40)
    print("Integration example complete!")
    print(f"Output directory: {pipeline.output_dir}")
    print(f"Scene configuration: {pipeline.output_dir / f'{scene_config.name}.yml'}")
    print("\nScene Summary:")
    print(f"  • Target: {config.aoi_size_km}km x {config.aoi_size_km}km @ {config.target_resolution_m}m")
    print(f"  • Buffer: {config.buffer_size_km}km x {config.buffer_size_km}km @ {config.buffer_resolution_m}m")
    print(f"  • Background: {config.background_material} @ {config.background_elevation}m elevation")
    
    return True


if __name__ == "__main__":
    print("S2GOS Simple Integration - Clean Workflow Demo")
    print("Demonstrates the refactored architecture:")
    print("  s2gos-generator: Scene generation")
    print("  s2gos-simulator: Simulation configuration and execution")
    print()
    
    success = simple_integration_example()
    
    if not success:
        print("\n✗ Example failed - check dependencies and data paths")