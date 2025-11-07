from s2gos_generator import SceneGenConfig, SceneGenerationPipeline
from upath import UPath


def simple_generation_example(config: SceneGenConfig):
    """Demonstrate complete S2GOS generation from configuration."""
    print("S2GOS Integration Example")
    print("=" * 60)
    print()

    # Step 1: Create and validate configuration
    print("Step 1: Validate config...")
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

    print("  Saved: scene_gen_config.json")

    print("\nStep 2: Generating scene with configuration...")

    try:
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
