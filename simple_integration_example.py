#!/usr/bin/env python3
"""Simple S2GOS Integration Example - Clean generator → simulator workflow."""

from pathlib import Path
from s2gos_generator.core import SceneGenerationConfig, SceneGenerationPipeline
from s2gos_simulator import create_default_render_config, EradiateSimulator, ERADIATE_AVAILABLE

# Available background material options:
# Vegetation: "treecover", "shrubland", "grassland", "cropland", "mangroves", "wetland"
# Non-vegetation: "concrete", "baresoil", "snow", "moss", "water"
# 
# Each material has physically-accurate spectral properties for realistic radiative transfer
BACKGROUND_MATERIAL = "water"  # Change this to customize background surface material


def simple_integration_example():
    """Demonstrate clean S2GOS integration: generate scene → run simulation."""
    print("S2GOS Simple Integration Example")
    print("=" * 40)
    print("Clean workflow: Scene Generation → Simulation")
    print()
    
    # Step 1: Generate Scene
    print("Step 1: Generating scene...")
    
    config = SceneGenerationConfig(
        # Geographic area specification
        center_lat=27.978497,
        center_lon=-15.590282,
        aoi_size_km=10.0,
        
        # Data paths - update these to match your system
        dem_index_path=Path("/home/gonzalezm/s2gos/s2gos/packages/s2gos-generator/src/s2gos_generator/data/dem_index.feather"),
        dem_root_dir=Path("/media/DATA/DEM"),
        landcover_index_path=Path("/home/gonzalezm/s2gos/s2gos/packages/s2gos-generator/src/s2gos_generator/data/landcover_index.feather"), 
        landcover_root_dir=Path("/home/gonzalezm/Data"),
        
        output_dir=Path("./simple_integration_output"),
        scene_name="simple_integration_scene",
        target_resolution_m=30.0,    # High resolution for target area
        
        # Buffer area configuration - creates larger context around target
        enable_buffer=True,
        buffer_size_km=60.0,         # Total buffer area: 50km x 50km (extends 20km in each direction from 10km target)
        buffer_resolution_m=100.0,   # Lower resolution for buffer to keep manageable file sizes
        
        # Background surface configuration
        background_elevation=0.0,    # Sea level for ocean background (meters above sea level)
        background_material=BACKGROUND_MATERIAL,  # Material type for background surface
    )
    
    try:
        pipeline = SceneGenerationPipeline(config)
        scene_config = pipeline.run_full_pipeline()
        
        print(f"✓ Scene generated: {scene_config.name}")
        print(f"  Location: {scene_config.metadata.center_lat}, {scene_config.metadata.center_lon}")
        print(f"  Target area: {config.aoi_size_km}km x {config.aoi_size_km}km at {config.target_resolution_m}m resolution")
        print(f"  Buffer area: {config.buffer_size_km}km x {config.buffer_size_km}km at {config.buffer_resolution_m}m resolution")
        if scene_config.background:
            print(f"  Background: {scene_config.background.get('material', 'N/A')} at {scene_config.background.get('elevation', 'N/A')}m elevation")
        print(f"  Assets: {pipeline.output_dir}")
        
    except Exception as e:
        print(f"✗ Scene generation failed: {e}")
        print("Check data paths and ensure required files are accessible")
        return False
    
    # Step 2: Configure Simulation
    print("\nStep 2: Configuring simulation...")
    
    render_config = create_default_render_config(
        name="simple_integration",
        sensor_height=50000.0,  # 50km altitude
        sensor_resolution=[1024, 1024],
        spp=32,
        zenith=30.0,
        azimuth=180.0
    )
    
    print(f"✓ Simulation configured: {render_config.name}")
    print(f"  Camera height: {render_config.sensors[0].origin[2]/1000:.1f}km")
    print(f"  Resolution: {render_config.sensors[0].resolution}")
    
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
                print(f"✗ Simulation failed: {results['error']}")
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