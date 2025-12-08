#!/usr/bin/env python3
from sim_util import simple_simulation_example, simulation_config

if __name__ == "__main__":
    # Individual arguments can be accessed as attributes...
    print("S2GOS Simulation Demo")
    print()

    scene_name = "pnp"
    target_lat = -46.917
    target_lon = -72.450
    target_size = 10
    gmt_hour = 14
    spp = 8

    config = simulation_config(scene_name, target_lat, target_lon, target_size, gmt_hour, spp)
    success = simple_simulation_example(scene_name, config)

    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo encountered issues")
        print("Check dependencies and data paths")
