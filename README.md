# S2GOS-apps

Use case applications for the S2GOS software packages, integrating scene generation and simulation capabilities with OGC-API process workflows via EOzilla.

## Installation

Clone with submodules:

```bash
git clone https://github.com/s2gos-dev/s2gos-apps.git --recurse-submodules
cd s2gos-apps
```

Install using pixi:

```bash
pixi install
```

## Project Structure

```
s2gos-apps/
├── packages/              # S2GOS submodules
│   ├── s2gos-generator   # Scene generation
│   ├── s2gos-simulator   # Simulation engine
│   └── s2gos-utils       # Utilities
├── src/s2gos_apps/
│   └── processes/        # EOzilla OGC-API processes
└── example/              # Usage examples
```

## Usage

See example in `./example/gobabeb.ipynb`.

## OGC-API Processes

EOzilla-integrated processes for S2GOS use cases are located in `src/s2gos_apps/processes/`.