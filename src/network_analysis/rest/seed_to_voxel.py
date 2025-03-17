import json
import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
from nibabel import Nifti1Image
from nilearn import plotting
from nilearn.maskers import NiftiMasker, NiftiSpheresMasker


def get_sub_dir(sub_id: str) -> str:
    """
    Get subject's GLM directory.
    This directory contains the tedana-processed BOLD images,
    confound files, and brain masks.

    Args:
        sub_id (str): Subject ID

    Returns:
        str: Path to subject's GLM directory
    """
    bids = "/oak/stanford/groups/russpold/data/network_grant/validation_BIDS"
    glm_dir = f"{bids}/derivatives/glm_data"
    return f'{glm_dir}/sub-{sub_id}'

def get_session_dirs(subj_dir: str) -> list[str]:
    """
    Get session directories for a subject.
    Exclude sessions 11 and 12 since they do
    not have resting state data.

    TODO: Improve handling for sessions without resting state data.

    Args:
        subj_dir (str): Path to subject's GLM directory

    Returns:
        list[str]: List of session directories
    """
    session_dirs = glob(f'{subj_dir}/ses-*')
    return [s for s in session_dirs if not s.endswith(('/ses-11', '/ses-12'))]

def get_files(ses_dir: str) -> tuple[str, str, str]:
    """
    Get BOLD, confound, and mask files for a session.

    Args:
        ses_dir (str): Path to session directory

    Returns:
        tuple[str, str, str]: BOLD, confound, and mask files
    """
    bolds = glob(f'{ses_dir}/func/*rest*T1w*optcom*')
    confounds = glob(f'{ses_dir}/func/*rest*confounds*')
    t1w_masks = glob(f'{ses_dir}/func/*rest*T1w*mask*')

    assert len(bolds) == len(confounds) == len(t1w_masks) == 1, (
        f"Lengths don't match: {len(bolds)}, {len(confounds)}, {len(t1w_masks)}"
    )

    return bolds[0], confounds[0], t1w_masks[0]


def plot_seed_time_series(
    seed_ts: np.ndarray,
    outdir: str,
    seed_name: str,
    outfile: str = "fig1.png"
) -> None:
    """
    Plot seed time series.

    Args:
        seed_ts (np.ndarray): Seed time series
        outdir (str): Path to output directory
        seed_name (str): Seed name
    """
    plt.figure(constrained_layout=True)
    plt.plot(seed_ts)
    plt.title(f"Seed time series ({seed_name})")
    plt.xlabel("Scan number")
    plt.ylabel("Normalized signal")
    print("saving to ", f"{outdir}/{outfile}")
    plt.savefig(f"{outdir}/{outfile}")
    plt.close()

def dump_json(data: dict, outdir: str) -> None:
    """
    Dump data to JSON file.

    Args:
        data (dict): Data to dump
        outdir (str): Path to output directory
    """
    with open(f"{outdir}/meta.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

def add_metadata(
    seed_ts: np.ndarray,
    brain_ts: np.ndarray,
    seed_to_voxel_correlations: np.ndarray,
    seed_coords: list[tuple[int, int, int]],
    seed_name: str
) -> dict:
    """
    Return metadata from time series and seed 
    correlations.

    Args:
        seed_ts (np.ndarray): Seed time series
        brain_ts (np.ndarray): Brain time series
        seed_to_voxel_correlations (np.ndarray): Seed-to-voxel correlations
        seed_coords (list[tuple[int, int, int]]): Seed coordinates
        seed_name (str): Seed name
    Returns:
        dict: Metadata
    """
    return {
        "seed_time_series_shape": seed_ts.shape,
        "brain_time_series_shape": brain_ts.shape,
        "seed_to_voxel_correlations_shape": seed_to_voxel_correlations.shape,
        "min_seed_to_voxel_correlation": seed_to_voxel_correlations.min(),
        "max_seed_to_voxel_correlation": seed_to_voxel_correlations.max(),
        "seed_coords": seed_coords,
        "seed_name": seed_name,
    }


def plot_voxel_time_series(
    brain_ts: np.ndarray,
    outdir: str,
    voxel_indices: list[int] = [10, 45, 100, 5000, 10000],
    outfile: str = "fig2.png"
) -> None:
    """
    Plot brain time series.

    Args:
        brain_ts (np.ndarray): Brain time series
        outdir (str): Path to output directory
        voxel_indices (list[int]): Indices of voxels to plot
    """
    plt.figure(constrained_layout=True)
    plt.plot(brain_ts[:, voxel_indices])
    plt.title(f"Time series from {len(voxel_indices)} voxels")
    plt.xlabel("Scan number")
    plt.ylabel("Normalized signal")
    plt.savefig(f"{outdir}/{outfile}")
    plt.close()

def plot_seed_to_voxel_correlation(
    seed_to_voxel_correlations_img: Nifti1Image,
    outdir: str,
    seed_coords: list[tuple[int, int, int]],
    outfile: str = "seed_correlation.pdf",
    marker_size: int = 10,
    threshold: float = 0.5,
    vmax: float = 1,
    title: str = "Seed-to-voxel correlation"
) -> None:
    """
    Plot seed-to-voxel correlation.

    Args:
        seed_to_voxel_correlations_img (Nifti1Image): Seed-to-voxel correlation image
        outdir (str): Path to output directory
        seed_coords (list[tuple[int, int, int]]): Seed coordinates
        seed_name (str): Seed name
        marker_size (int, optional): Marker size. Defaults to 10.
        threshold (float, optional): Threshold. Defaults to 0.5.
        vmax (float, optional): Maximum value. Defaults to 1.
        title (str, optional): Title. Defaults to "Seed-to-voxel correlation
            ({seed_name} seed)".
    """
    display = plotting.plot_stat_map(
        seed_to_voxel_correlations_img,
        threshold=threshold,
        vmax=vmax,
        cut_coords=seed_coords[0],
        title=title,
    )
    display.add_markers(
        marker_coords=seed_coords, marker_color="g", marker_size=marker_size
    )
    display.savefig(f"{outdir}/{outfile}")
    display.close()

def main():
    print("Running resting state analysis...")
    subj_id = "s1273"
    sub_dir = get_sub_dir(subj_id)
    session_dirs = get_session_dirs(sub_dir)
    session_dirs.sort()

    # Seed location and name
    seed_coords = [(0, -52, 18)]
    seed_name = "PCC"

    for ses_dir in session_dirs:
        ses_id = os.path.basename(ses_dir)

        print(f"Processing {subj_id} - {ses_id}")

        bold, confound, mask = get_files(ses_dir)

        # Prepare output directory for figs
        outdir = f"results/{subj_id}/{ses_id}"
        os.makedirs(outdir, exist_ok=True)

        seed_masker = NiftiSpheresMasker(
            seed_coords,
            mask_img=mask,
            radius=8,
            detrend=True,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            t_r=1.49,
            memory="nilearn_cache",
            memory_level=1,
            verbose=0,
        )

        seed_time_series = seed_masker.fit_transform(
            bold, confounds=[confound]
        )

        brain_masker = NiftiMasker(
            mask_img=mask,
            smoothing_fwhm=6,
            detrend=True,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            t_r=1.49,
            memory="nilearn_cache",
            memory_level=1,
            verbose=0,
        )

        brain_time_series = brain_masker.fit_transform(
            bold, confounds=[confound]
        )

        print(f"Seed time series shape: ({seed_time_series.shape})")
        print(f"Brain time series shape: ({brain_time_series.shape})")

        plot_seed_time_series(seed_time_series, outdir, seed_name)
        plot_voxel_time_series(brain_time_series, outdir)

        # Correlations between seed and target
        seed_to_voxel_correlations = (
            np.dot(brain_time_series.T, seed_time_series) / seed_time_series.shape[0]
        )

        print(
            "Seed-to-voxel correlation shape: ({}, {})".format(
                *seed_to_voxel_correlations.shape
            )
        )
        print(
            f"Seed-to-voxel correlation: "
            f"min = {seed_to_voxel_correlations.min():.3f}; "
            f"max = {seed_to_voxel_correlations.max():.3f}"
        )

        seed_to_voxel_correlations_img = brain_masker.inverse_transform(
            seed_to_voxel_correlations.T
        )

        plot_seed_to_voxel_correlation(
            seed_to_voxel_correlations_img,
            outdir,
            seed_coords,
        )

        metadata = add_metadata(
            seed_time_series,
            brain_time_series,
            seed_to_voxel_correlations,
            seed_coords,
            seed_name
        )
        dump_json(metadata, outdir)

if __name__ == "__main__":
    main()

