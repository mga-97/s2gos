"""
Run HYPSTAR simulations from real L2A dataset.

Workflow:
1. Load HYPSTAR L2A NetCDF data.
2. Generate the 3D Scene (Atmosphere + Surface + XML objects).
3. Loop through dataset series: configure geometry, run sim, save output.
"""

import shutil
import traceback
from pathlib import Path
from datetime import datetime, timezone
from upath import UPath
import xarray as xr

# S2GOS / Eradiate Imports
from s2gos_generator import create_scene_config
from s2gos_generator.core import SceneGenerationPipeline
from s2gos_generator.core.config import (
    MolecularAtmosphereConfig,
    ThermophysicalConfig,
    AbsorptionDatabase,
    ParticleLayerConfig,
    ExponentialDistribution,
    MaterialRegion,
    XmlSceneConfig,
)
from s2gos_generator.core.region_geometry import RectangleGeometry
from s2gos_simulator.config import (
    SimulationConfig,
    DirectionalIllumination,
    IrradianceConfig,
    HCRFConfig,
    HemisphericalMeasurementLocation,
    SpectralResponse,
    GroundSensor,
    GroundInstrumentType,
    AngularFromOriginViewing,
    HypstarPostProcessingConfig,
    HCRFPostProcessingConfig,
)
from s2gos_simulator.backends.eradiate.backend import (
    EradiateBackend,
    ERADIATE_AVAILABLE,
)

# ==============================================================================
# 1. USER CONFIGURATION
# ==============================================================================

# Input / Output Paths
HYPSTAR_L2A_PATH = ""
OUTPUT_DIR = Path("./hypstar_simulation_output")
SCENE_NAME = "hypstar_gobabeb"

# Data Dependencies
PATHS = {
    "hamster": "",
    "thermo": "",
    "aerosol": "",
    "rpv": "",
    "cams": "",
    "kinne": "",
    "mast": "",
    "fence": "",
}

# Settings
SERIES_INDICES = [1, 24]  # List of indices or None for all
TARGET_COORDS = (-23.6015417, 15.1258696)  # (Lat, Lon)
SENSOR_ORIGIN = [0.022914, 1.16748, 10.5269]
IRR_HEIGHT = 13.0
SENSOR_SAMPLES = 4
IRR_SAMPLES = 4


# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================


def get_geometry_and_time(ds: xr.Dataset, idx: int) -> dict:
    """Extracts timestamp and converts HYPSTAR angles to Eradiate convention."""
    vza_hyp = float(ds.viewing_zenith_angle.values[idx])
    vaa_hyp = float(ds.viewing_azimuth_angle.values[idx])
    sza_hyp = float(ds.solar_zenith_angle.values[idx])
    saa_hyp = float(ds.solar_azimuth_angle.values[idx])
    ts_unix = int(ds.acquisition_time.values[idx])

    return {
        "vza": 180.0 - vza_hyp,
        "vaa": (90.0 - vaa_hyp) % 360.0,
        "sza": sza_hyp,
        "saa": (90.0 - saa_hyp) % 360.0,
        "dt": datetime.fromtimestamp(ts_unix, timezone.utc),
    }


def get_atmosphere_params(timestamp_dt: datetime) -> tuple[float, float]:
    """Retrieves AOD and aerosol height from climatology files."""
    gobabeb_ds = xr.open_dataset(PATHS["cams"])
    kinne_ds = xr.open_dataset(PATHS["kinne"])

    ts_naive = timestamp_dt.replace(tzinfo=None)
    aod = float(
        gobabeb_ds.aod550.dropna(dim="time").sel(time=ts_naive, method="nearest").values
    )

    month = timestamp_dt.month - 1
    kinne_loc = kinne_ds.sel(
        lat=TARGET_COORDS[0], lon=TARGET_COORDS[1], method="nearest"
    ).isel(time=month)

    aerosol_height = 2000.0  # Fallback
    for i in range(len(kinne_loc.lay)):
        if float(kinne_loc.AODt_frac[: i + 1].sum()) >= 0.92:
            aerosol_height = float(kinne_loc.Zl_top.isel(lay=i).values)
            break

    return aod, aerosol_height


def load_hcrf_zarr(zarr_path: Path, idx: int, geo: dict, series_id: int) -> xr.Dataset:
    """Load single HCRF Zarr file and add HYPERNETS-compatible coordinates.

    Args:
        zarr_path: Path to the Zarr directory
        idx: Series index from reference dataset
        geo: Geometry dictionary with viewing/solar angles and timestamp
        series_id: Actual series_id from reference dataset

    Returns:
        Dataset with reflectance and coordinate variables
    """
    ds = xr.open_zarr(zarr_path)

    if "x_index" in ds.dims or "y_index" in ds.dims:
        spatial_dims = [d for d in ["x_index", "y_index"] if d in ds.dims]
        ds = ds.mean(dim=spatial_dims)

    ds = ds.rename({"w": "wavelength", "hcrf": "reflectance"})

    ds = ds.assign_coords(
        {
            "viewing_azimuth_angle": geo["vaa"],
            "viewing_zenith_angle": geo["vza"],
            "solar_azimuth_angle": geo["saa"],
            "solar_zenith_angle": geo["sza"],
            "acquisition_time": geo["dt"].timestamp(),
            "series_id": series_id,
        }
    )

    return ds


def combine_hcrf_results(
    output_dir: Path, indices: list, ds_ref: xr.Dataset
) -> xr.Dataset:
    """Combine all HCRF Zarr files into single HYPERNETS-format NetCDF.

    Args:
        output_dir: Directory containing copied Zarr files
        indices: List of series indices to include
        ds_ref: Reference HYPSTAR dataset (for series_id mapping)

    Returns:
        Combined dataset with all series
    """
    import numpy as np

    datasets = []

    for idx in indices:
        series_id = int(ds_ref.series_id.values[idx])
        geo = get_geometry_and_time(ds_ref, idx)

        zarr_path = output_dir / f"hcrf_series_{idx:02d}.zarr"
        if not zarr_path.exists():
            print(
                f"  ⚠ Warning: Missing Zarr file for series {idx} (series_id={series_id})"
            )
            continue

        ds = load_hcrf_zarr(zarr_path, idx, geo, series_id)
        datasets.append(ds)

    if not datasets:
        raise ValueError("No HCRF files found to combine")

    combined = xr.concat(datasets, dim="series")

    combined["bandwidth"] = xr.DataArray(
        np.zeros(len(combined.wavelength)),
        dims=["wavelength"],
        coords={"wavelength": combined.wavelength},
    )

    combined.attrs = {
        "title": "S2GOS simulated HYPSTAR observations",
        "simulator": "S2GOS (Synthetic Scene Generation and Observation Simulation)",
        "description": "Simulated HCRF measurements matching HYPERNETS protocol",
        "created": datetime.now(timezone.utc).isoformat(),
        "reference_dataset": Path(HYPSTAR_L2A_PATH).name,
    }

    return combined


# ==============================================================================
# 3. SCENE & SIMULATION SETUP
# ==============================================================================


def build_scene_config() -> object:
    """Constructs the scene gen configuration."""
    config = create_scene_config(
        scene_name=SCENE_NAME,
        center_lat=TARGET_COORDS[0],
        center_lon=TARGET_COORDS[1],
        aoi_size_km=4.0,
        target_resolution_m=10.0,
        output_dir=UPath(OUTPUT_DIR) / "scene",
        description="HYPSTAR validation scene",
    )

    config.enable_buffer = True
    config.buffer_size_km = 60.0
    config.buffer_resolution_m = 60.0
    config.enable_background = True
    config.background_size_km = 100
    config.background_resolution_m = 200.0

    config.enable_hamster_albedo(PATHS["hamster"], "albedo", fallback_on_error=True)

    config.region_material_defs["gobabeb_measured_rpv"] = {
        "type": "rpv",
        "rho_0": {"path": PATHS["rpv"], "variable": "rho_0"},
        "k": {"path": PATHS["rpv"], "variable": "k"},
        "Theta": {"path": PATHS["rpv"], "variable": "Theta"},
        "rho_c": {"path": PATHS["rpv"], "variable": "rho_c"},
    }
    config.material_regions.append(
        MaterialRegion(
            region_id="center_rpv",
            geometry=RectangleGeometry(
                center_x=0.0, center_y=0.0, width_m=1500.0, height_m=1500.0
            ).model_dump(),
            material_name="gobabeb_measured_rpv",
            priority=10,
            applies_to=["target"],
        )
    )

    config.xml_scenes.append(
        XmlSceneConfig(
            xml_path=PATHS["mast"],
            base_coordinate=(TARGET_COORDS[1], TARGET_COORDS[0]),
            elevation_offset=-0.1,
        )
    )
    config.xml_scenes.append(
        XmlSceneConfig(
            xml_path=PATHS["fence"], base_coordinate=(15.1253501, -23.6011482)
        )
    )

    # Atmosphere (Fixed reference time)
    atm_time = datetime(2022, 5, 17, 9, 45, 4, tzinfo=timezone.utc)
    aod, aer_h = get_atmosphere_params(atm_time)
    print(f"  Atmosphere Params: AOD={aod:.3f}, Height={aer_h:.1f}m")

    config.set_atmosphere_heterogeneous(
        MolecularAtmosphereConfig(
            thermoprops=ThermophysicalConfig(
                identifier=None, thermoprops_file=UPath(PATHS["thermo"])
            ),
            absorption_database=AbsorptionDatabase.MYCENA,
            has_absorption=True,
            has_scattering=True,
        ),
        [
            ParticleLayerConfig(
                aerosol_dataset=PATHS["aerosol"],
                optical_thickness=aod,
                altitude_bottom=500.0,
                altitude_top=500.0 + aer_h,
                distribution=ExponentialDistribution(rate=5.0),
                has_absorption=True,
            )
        ],
    )

    if errors := config.validate_configuration():
        raise ValueError(f"Config Errors: {errors}")
    return config


def build_sim_config(idx: int, geo: dict) -> SimulationConfig:
    """Creates the simulation config for a specific time/geometry."""
    return SimulationConfig(
        name=f"hypstar_series_{idx:02d}",
        description=f"Series {idx} at {geo['dt']}",
        # Sun Position
        illumination=DirectionalIllumination(
            id=f"sun_series_{idx:02d}",
            zenith=geo["sza"],
            azimuth=geo["saa"],
            irradiance_dataset="coddington_2022-1_nm",
        ),
        # Sensors
        sensors=[
            GroundSensor(
                id=f"hypstar_series_{idx:02d}",
                instrument=GroundInstrumentType.HYPSTAR,
                viewing=AngularFromOriginViewing(
                    origin=SENSOR_ORIGIN,
                    zenith=geo["vza"],
                    azimuth=geo["vaa"],
                    up=[0, 0, 1] if geo["vza"] != 180 else [0, 1, 0],
                    terrain_relative_height=True,
                ),
                fov=5.0,
                resolution=[32, 32],
                samples_per_pixel=SENSOR_SAMPLES,
                srf=SpectralResponse(type="uniform", wmin=380, wmax=1680),
                hypstar_post_processing=HypstarPostProcessingConfig(
                    apply_srf=True,
                    fwhm_vnir_nm=3.0,
                    fwhm_swir_nm=10.0,
                    spatial_averaging=True,
                    real_reference_file=HYPSTAR_L2A_PATH,
                    wavelength_variable="wavelength",
                ),
            )
        ],
        # Measurements (Irradiance + HCRF)
        measurements=[
            IrradianceConfig(
                id=f"irradiance_series_{idx:02d}",
                location=HemisphericalMeasurementLocation(
                    target_lat=TARGET_COORDS[0],
                    target_lon=TARGET_COORDS[1],
                    height_offset_m=IRR_HEIGHT,
                    srf=SpectralResponse(type="uniform", wmin=380, wmax=1680),
                    samples_per_pixel=IRR_SAMPLES,
                ),
            ),
            HCRFConfig(
                id=f"hcrf_series_{idx:02d}",
                radiance_sensor_id=f"hypstar_series_{idx:02d}",
                irradiance_measurement_id=f"irradiance_series_{idx:02d}",
                post_processing=HCRFPostProcessingConfig(
                    compute_spatial_average=True, apply_srf_convolution=False
                ),
            ),
        ],
        backend_hints={"eradiate": {"mode": "ckd"}},
    )


# ==============================================================================
# 4. MAIN EXECUTION
# ==============================================================================


def main():
    if not ERADIATE_AVAILABLE:
        raise RuntimeError("Eradiate is missing.")
    if not Path(HYPSTAR_L2A_PATH).exists():
        raise FileNotFoundError("L2A data missing.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== HYPSTAR Simulator | Output: {OUTPUT_DIR} ===")

    # 1. Load Data
    ds = xr.load_dataset(HYPSTAR_L2A_PATH)
    indices = SERIES_INDICES if SERIES_INDICES else list(range(len(ds.series)))
    print(f"[1/5] Loaded dataset. Processing {len(indices)} series.")

    # 2. Generate Scene
    print("\n[2/5] Generating Scene...")
    scene_config = build_scene_config()
    pipeline = SceneGenerationPipeline(scene_config)
    scene_desc = pipeline.run_full_pipeline()
    scene_config.to_json(OUTPUT_DIR / "scene_config.json")

    # 3. Run Simulations
    print("\n[3/5] Running Simulations...")
    for i, idx in enumerate(indices):
        geo = get_geometry_and_time(ds, idx)
        print(
            f"  > Series {idx} ({i + 1}/{len(indices)}) | {geo['dt']} | SZA:{geo['sza']:.1f} VZA:{geo['vza']:.1f}"
        )

        try:
            sim_config = build_sim_config(idx, geo)
            sim_config.to_json(OUTPUT_DIR / f"config_{idx:02d}.json")

            backend = EradiateBackend(sim_config)
            backend.run_simulation(
                scene_desc, scene_config.scene_output_dir, plot_image=False
            )

            src = (
                scene_config.scene_output_dir
                / "eradiate_renders"
                / "derived_results"
                / f"hypstar_series_{idx:02d}_hcrf_series_{idx:02d}.zarr"
            )
            dst = OUTPUT_DIR / f"hcrf_series_{idx:02d}.zarr"
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"Copied to: {dst.name}")
            else:
                print("Error: Output file not created.")

        except Exception:
            print(f"Failed: {traceback.format_exc().splitlines()[-1]}")

    # 4. Combine Results into Single NetCDF
    print("\n[4/5] Combining results into HYPERNETS format...")
    try:
        combined_ds = combine_hcrf_results(OUTPUT_DIR, indices, ds)
        output_nc = OUTPUT_DIR / f"{SCENE_NAME}_combined_hcrf.nc"
        combined_ds.to_netcdf(output_nc, mode="w")
        print(f"  ✓ Saved combined NetCDF: {output_nc.name}")
        print(f"    - Wavelengths: {len(combined_ds.wavelength)}")
        print(f"    - Series: {len(combined_ds.series)}")
    except Exception as e:
        print(f"  ✗ Failed to combine results: {e}")

    print("\n[5/5] Finished.")


if __name__ == "__main__":
    main()
