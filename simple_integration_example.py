#!/usr/bin/env python3
"""Simple S2GOS Integration Example - Clean generator → simulator workflow."""

from pathlib import Path
from s2gos_generator.core import SceneGenerationConfig, SceneGenerationPipeline
from s2gos_simulator import (
    create_default_render_config, EradiateSimulator, ERADIATE_AVAILABLE,
    PerspectiveSensor, DistantMeasure, MultiDistantMeasure, 
    srf_rgb, srf_visible, srf_multispectral, srf_dataset,
    DirectionalIllumination, SimulationConfig
)

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
        center_lat=27.978497,
        center_lon=-15.590282,
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
    
    # Create different sensor types with different SRF configurations
    sensors = [
        # Perspective camera with RGB bands
        PerspectiveSensor(
            id="rgb_camera",
            origin=[0, 0, 50000],  # 50km altitude
            target=[0, 0, 0],
            resolution=[1024, 1024],
            srf=srf_rgb(),  # RGB delta SRF
            spp=32
        ),
        
        # Distant measurement with visible spectrum
        DistantMeasure.from_angles(
            id="visible_distant",
            zenith=15.0,
            azimuth=45.0,
            srf=srf_rgb(),  # Uniform SRF 400-700nm
            spp=64
        ),
        
        # Multi-angle measurement for BRDF with custom bands
        MultiDistantMeasure.hplane(
            zeniths=[0, 15, 30, 45],  # Multiple viewing angles
            azimuth=0.0,              # Principal plane
            id="brdf_measurement",
            srf=srf_multispectral([443, 550, 670, 865]),  # Blue, Green, Red, NIR
            spp=128
        ),
        
        # # Dataset SRF example (Sentinel-2A MSI band 4)
        # DistantMeasure.from_angles(
        #     id="sentinel2_band",
        #     zenith=0.0,  # Nadir
        #     azimuth=0.0,
        #     srf="sentinel_2a-msi-4",  # Dataset SRF as string
        #     spp=64
        # )
    ]
    
    # Create custom render configuration
    render_config = SimulationConfig(
        name="enhanced_simulation",
        illumination=DirectionalIllumination(zenith=30.0, azimuth=180.0),
        sensors=sensors
    )
    
    print(f"Simulation configured: {render_config.name}")
    print(f"Number of sensors: {len(render_config.sensors)}")
    for i, sensor in enumerate(render_config.sensors):
        srf_info = "dict" if isinstance(sensor.srf, dict) else "string" if isinstance(sensor.srf, str) else "unknown"
        print(f"  {i+1}. {sensor.id} ({sensor.type}) - SRF: {srf_info}")
    
    # Step 3: Run Simulation
    if ERADIATE_AVAILABLE:
        print("\nStep 3: Running Eradiate simulation...")
        
        try:
            simulator = EradiateSimulator(render_config)
            results = simulator.run_simulation(scene_config, pipeline.output_dir)
            
            if results["success"]:
                print(f"Simulation complete!")
                print(f"  Raw results: {results['raw_results']}")
                print(f"  RGB image: {results['rgb_image']}")
                print(f"  Output: {results['output_dir']}")
            else:
                print(f"Simulation failed: {results['error']}")
                return False
                
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
    print(f"\nScene Summary:")
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