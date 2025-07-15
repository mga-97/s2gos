import argparse  # New import
from pathlib import Path
from typing import Optional  # New import

from s2gos_generator.core import SceneGenerationPipeline
from s2gos_generator.core.config import SceneGenConfig
from s2gos_simulator.config import SimulationConfig
from s2gos_simulator.backends.eradiate_backend import (
    EradiateBackend,
    ERADIATE_AVAILABLE,
)


# The function is refactored to accept paths as arguments
def run_pipeline(scene_config_path: Path, sim_config_path: Optional[Path] = None):
    """
    Load configurations and run the scene generation and (optionally) simulation pipelines.

    Args:
        scene_config_path (Path): Path to the scene generation configuration JSON file.
        sim_config_path (Optional[Path]): Optional path to the simulation configuration JSON file.
    """
    print("S2GOS Pipeline from Configuration")
    print("=" * 60)

    # --- Step 1: Load Scene Configuration ---
    print("\nStep 1: Loading Scene Configuration...")
    if not scene_config_path.exists():
        print(f"Scene config file not found: {scene_config_path}")
        return False

    try:
        scene_gen_config = SceneGenConfig.from_json(scene_config_path)
        print(f"Loaded scene config from {scene_config_path}")
    except Exception as e:
        print(f"Failed to load scene configuration: {e}")
        return False

    # --- Step 2: Load Simulation Configuration (if provided) ---
    simulation_config = None
    if sim_config_path:
        print("\nStep 2: Loading Simulation Configuration...")
        if not sim_config_path.exists():
            print(f"Simulation config file not found: {sim_config_path}")
            return False

        try:
            simulation_config = SimulationConfig.from_json(sim_config_path)
            print(f"Loaded simulation config from {sim_config_path}")
        except Exception as e:
            print(f"Failed to load simulation configuration: {e}")
            return False
    else:
        print("\nStep 2: No simulation configuration provided. Skipping simulation.")

    # --- Step 3: Generate Scene ---
    print(f"\nStep 3: Generating scene from config '{scene_gen_config.scene_name}'...")

    try:
        pipeline = SceneGenerationPipeline(scene_gen_config)
        scene_description = pipeline.run_full_pipeline()

        print("\nScene generation completed")

    except Exception as e:
        print(f"Scene generation failed: {e}")
        scene_description = None
        return False

    # --- Step 4: Run Simulation (if configured and possible) ---
    if simulation_config and ERADIATE_AVAILABLE and scene_description:
        print("\nStep 4: Running simulation from deserialized config...")

        try:
            simulator = EradiateBackend(simulation_config)
            simulator.run_simulation(
                scene_description,
                scene_gen_config.scene_output_dir,
                plot_image=True,
                id_to_plot="uav_rgb_camera",
            )
            print("\nSimulation completed successfully!")

        except Exception as e:
            print(f"Simulation failed: {e}")
            print(
                "   This might be expected if eradiate is not available or not configured properly"
            )
            return False

    elif simulation_config and not ERADIATE_AVAILABLE:
        print("\nStep 4: Skipping simulation (eradiate not available)")
        print(" Install eradiate to run full simulation pipeline")

    elif simulation_config and not scene_description:
        print("\nStep 4: Skipping simulation (scene generation failed)")

    return True


# --- Main execution block is updated to handle command-line arguments ---
if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Run S2GOS scene generation and simulation from configuration files."
    )
    parser.add_argument(
        "scene_config",
        type=Path,
        help="Path to the scene configuration JSON file (e.g., scene_config.json).",
    )
    parser.add_argument(
        "sim_config",
        type=Path,
        nargs="?",  # Makes this argument optional
        default=None,
        help="Optional: Path to the simulation configuration JSON file (e.g., simulation_config.json).",
    )
    args = parser.parse_args()

    # Run the main pipeline with the parsed arguments
    success = run_pipeline(args.scene_config, args.sim_config)

    if success:
        print("\n SUCCESS!")
    else:
        print("\Failed - see errors above.")
