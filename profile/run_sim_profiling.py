#!/usr/bin/env python3
"""
Script to run simulation memory profiling with multiple parameter combinations.
"""
import subprocess
import itertools
from pathlib import Path

# Define parameter arrays to test
TARGET_SIZES = [1, 2, 5, 10, 20, 50]  # Adjust these values as needed
VEG_DENSITIES = [0]  # Adjust if you want to test different densities
BUFFERS = [0, 1]  # 0 = no buffer, 1 = with buffer
BACKGROUNDS = [0, 1]  # 0 = no background, 1 = with background

def main():
    # Ensure profile directory exists
    profile_dir = Path("./profile/simulation")
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Generate all combinations
    combinations = list(itertools.product(TARGET_SIZES, VEG_DENSITIES, BUFFERS, BACKGROUNDS))

    print(f"Running {len(combinations)} simulation profiling combinations...")
    print("-" * 60)

    for idx, (size, density, buffer, background) in enumerate(combinations, 1):
        print(f"\n[{idx}/{len(combinations)}] Running with:")
        print(f"  Size: {size}, Density: {density}, Buffer: {buffer}, Background: {background}")

        try:
            # Run the bash script with the current combination
            result = subprocess.run(
                ["bash", "memray_run_sim.sh", str(size), str(density), str(buffer), str(background)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"  ✓ Completed successfully")

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed with return code {e.returncode}")
            print(f"  Error output: {e.stderr}")
            # Continue with next combination even if one fails
            continue

    print("\n" + "=" * 60)
    print("All profiling runs completed!")
    print(f"Results saved in: {profile_dir}")

if __name__ == "__main__":
    main()
