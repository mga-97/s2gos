#!/usr/bin/env python3
"""
Extract profiling statistics from memray HTML flamegraph files.

This script parses all memray flamegraph HTML files in the profile/generation
and profile/simulation directories, extracting Duration and Peak memory usage
statistics from the modal-body div.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd


def parse_filename(filename: str) -> Optional[Dict[str, any]]:
    """
    Parse memray flamegraph filename to extract parameters.

    Expected format: memray-flamegraph-pnp_S<target_size>_D<density>[_noBU][_noBa].html

    Args:
        filename: The HTML filename to parse

    Returns:
        Dictionary with parsed parameters or None if parsing fails
    """
    pattern = r"memray-flamegraph-pnp_S(\d+)_D(\d+)(_noBU)?(_noBa)?.*\.html"
    match = re.match(pattern, filename)

    if not match:
        return None

    target_size, density, no_buffer, no_background = match.groups()

    return {
        "target_size": int(target_size),
        "density": int(density),
        "has_buffer": no_buffer is None,  # If _noBU is absent, buffer is present
        "has_background": no_background is None,  # If _noBa is absent, background is present
    }


def extract_stats_from_html(html_path: Path) -> Optional[Tuple[str, str]]:
    """
    Extract Duration and Peak memory usage from HTML file.

    Args:
        html_path: Path to the HTML file

    Returns:
        Tuple of (duration, peak_memory) or None if extraction fails
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the modal-body section
        modal_body_match = re.search(
            r'<div class="modal-body">(.*?)</div>',
            content,
            re.DOTALL
        )

        if not modal_body_match:
            return None

        modal_body = modal_body_match.group(1)

        # Extract Duration
        duration_match = re.search(r'Duration:\s*([0-9:\.]+)', modal_body)
        duration = duration_match.group(1) if duration_match else None

        # Extract Peak memory usage
        memory_match = re.search(r'Peak memory usage:\s*([\d\.]+ [A-Z]+)', modal_body)
        peak_memory = memory_match.group(1) if memory_match else None

        # Convert peak memory to GB
        if peak_memory:
            value, unit = peak_memory.split()
            value = float(value)
            if unit == 'MB':
                value /= 1000
            elif unit == 'KB':
                value /= (1000 * 1000)
            peak_memory = value

        return (duration, peak_memory)

    except Exception as e:
        print(f"Error processing {html_path}: {e}")
        return None


def process_profile_directory(profile_type: str, base_dir: Path) -> pd.DataFrame:
    """
    Process all memray HTML files in a profile directory.

    Args:
        profile_type: Either 'generation' or 'simulation'
        base_dir: Base directory containing profile subdirectories

    Returns:
        DataFrame with extracted statistics
    """
    profile_dir = base_dir / profile_type

    if not profile_dir.exists():
        print(f"Warning: Directory {profile_dir} does not exist")
        return pd.DataFrame()

    data = []

    # Find all memray flamegraph HTML files
    html_files = profile_dir.glob("memray-flamegraph-*.html")

    for html_file in sorted(html_files):
        print(f"Processing {profile_type}/{html_file.name}...")

        # Parse filename
        params = parse_filename(html_file.name)
        if params is None:
            print(f"  Warning: Could not parse filename {html_file.name}")
            continue

        # Extract stats
        stats = extract_stats_from_html(html_file)
        if stats is None:
            print(f"  Warning: Could not extract stats from {html_file.name}")
            continue

        duration, peak_memory = stats

        # Create row
        row = {
            "target_size": params["target_size"],
            "density": params["density"],
            "has_buffer": params["has_buffer"],
            "has_background": params["has_background"],
            "duration": duration,
            "peak_memory": peak_memory,
        }

        data.append(row)

    return pd.DataFrame(data)


def main():
    """Main function to extract stats from all memray HTML files."""
    # Get the profile directory
    base_dir = Path(__file__).parent / "profile"

    # Process generation directory
    print("Processing generation profiles...")
    # generation_df = process_profile_directory("generation", base_dir)
    # generation_df = generation_df.sort_values(
    #     by=["target_size", "density", "has_buffer", "has_background"]
    # ).reset_index(drop=True)

    # Process simulation directory
    print("\nProcessing simulation profiles...")
    simulation_df = process_profile_directory("simulation", base_dir)
    simulation_df = simulation_df.sort_values(
        by=["target_size", "density", "has_buffer", "has_background"]
    ).reset_index(drop=True)

    # Save to separate CSV files
    # generation_output = Path(__file__).parent / "memray_generation_stats.csv"
    simulation_output = Path(__file__).parent / "memray_simulation_opt_stats.csv"

    # generation_df.to_csv(generation_output, index=False)
    simulation_df.to_csv(simulation_output, index=False)

    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    # print(f"Generation records: {len(generation_df)}")
    # print(f"  Output saved to: {generation_output}")
    print(f"Simulation records: {len(simulation_df)}")
    print(f"  Output saved to: {simulation_output}")
    print(f"{'='*60}\n")

    # Display summaries
    print("Generation DataFrame:")
    # print(generation_df.head(10))
    print(f"\nSimulation DataFrame:")
    print(simulation_df.head(10))


if __name__ == "__main__":
    main()
