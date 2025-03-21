import json
import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
from nibabel import Nifti1Image
from nilearn import plotting
from nilearn.maskers import NiftiMasker, NiftiSpheresMasker
from nilearn.image import load_img, get_data

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

def dump_json(data: dict, outdir: str, filename: str = "meta.json") -> None:
    """
    Dump data to JSON file.

    Args:
        data (dict): Data to dump
        outdir (str): Path to output directory
        filename (str): Name of the JSON file
    """
    import os
    
    # Ensure the output directory exists
    os.makedirs(outdir, exist_ok=True)
    
    filepath = os.path.join(outdir, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)
    
    print(f"Saved metadata to {filepath}")

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

def create_sphere_mask(coords, radius_mm=10, mask_img=None, output_file="sphere.nii.gz"):
    """
    Simple method to create a binary mask with a sphere using math_img.
    
    Args:
        coords (tuple): (x, y, z) coordinates for the center of the sphere in mm
        radius_mm (int): Radius of the sphere in mm
        mask_img (str or NiftiImage): Brain mask to define the space
        output_file (str): Path to save the output sphere mask
        
    Returns:
        str: Path to the saved sphere mask
    """
    from nilearn import image, plotting
    import numpy as np
    from nibabel import Nifti1Image
    import os
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Load the mask image if it's a string
    if isinstance(mask_img, str):
        mask_img = load_img(mask_img)
    
    # Get shape and affine from mask image
    shape = mask_img.shape
    affine = mask_img.affine
    
    # Create coordinate grids in voxel space
    i, j, k = np.meshgrid(
        np.arange(shape[0]),
        np.arange(shape[1]),
        np.arange(shape[2]),
        indexing='ij'
    )
    
    # Convert the seed coordinates from mm to voxel coordinates
    voxel_coords = np.linalg.inv(affine).dot(
        np.hstack((coords[0], coords[1], coords[2], 1))
    )[:3]
    
    # Calculate the Euclidean distance from each voxel to the seed (in voxel space)
    # Then transform that distance to mm space using the voxel dimensions
    voxel_size = np.sqrt(np.sum(affine[:3, :3]**2, axis=0))
    distances = np.sqrt(
        ((i - voxel_coords[0]) * voxel_size[0])**2 +
        ((j - voxel_coords[1]) * voxel_size[1])**2 +
        ((k - voxel_coords[2]) * voxel_size[2])**2
    )
    
    # Create the sphere mask
    sphere_data = distances <= radius_mm
    
    # Apply the brain mask if provided
    if mask_img is not None:
        brain_mask_data = image.get_data(mask_img).astype(bool)
        sphere_data = sphere_data & brain_mask_data
    
    # Create a Nifti image and save it
    sphere_img = Nifti1Image(sphere_data.astype(np.int16), affine)
    sphere_img.to_filename(output_file)

    # Create the plot and save it to a file
    display = plotting.plot_roi(
        output_file, 
        title=f"Sphere mask (radius={radius_mm}mm) at {coords}",
        cut_coords=coords  # Center view on the sphere coordinates
    )
    
    # Save the figure and close the display
    plot_file = output_file.replace(".nii.gz", "_plot.png")
    display.savefig(plot_file)
    display.close()
    
    print(f"Sphere mask saved to {output_file}")
    print(f"Visualization saved to {plot_file}")
    
    return output_file

def create_exclusion_mask(mask_img, sphere_mask_img, output_file="exclusion_mask.nii.gz"):
    """
    Create a mask that excludes the voxels in the sphere mask.
    
    Args:
        mask_img (str or NiftiImage): Original brain mask
        sphere_mask_img (str or NiftiImage): Sphere mask to exclude
        output_file (str): Path to save the output exclusion mask
        
    Returns:
        str: Path to the saved exclusion mask
    """
    from nilearn import image
    import numpy as np
    from nibabel import Nifti1Image
    
    # Load images if they're strings
    if isinstance(mask_img, str):
        mask_img = load_img(mask_img)
    if isinstance(sphere_mask_img, str):
        sphere_mask_img = load_img(sphere_mask_img)
    
    # Get data arrays and convert to boolean
    mask_data = get_data(mask_img).astype(bool)
    sphere_data = get_data(sphere_mask_img).astype(bool)
    
    # Create the exclusion mask: keep all brain voxels EXCEPT those in the sphere
    exclusion_data = mask_data & ~sphere_data
    
    # Create a Nifti image and save it
    exclusion_img = Nifti1Image(exclusion_data.astype(np.int16), mask_img.affine)
    exclusion_img.to_filename(output_file)
    
    # Visualize the exclusion mask
    display = plotting.plot_roi(
        output_file,
        bg_img=mask_img,
        title=f"Exclusion mask (brain voxels minus sphere)"
    )
    
    # Save the visualization
    plot_file = output_file.replace(".nii.gz", "_plot.png")
    display.savefig(plot_file)
    display.close()
    
    print(f"Exclusion mask saved to {output_file}")
    print(f"Visualization saved to {plot_file}")
    
    return output_file

def create_visualization_with_exclusion(
    bg_img, 
    exclusion_mask, 
    seed_coords, 
    seed_radius, 
    exclusion_radius, 
    outdir, 
    seed_name
):
    """
    Create a visualization showing the seed region and excluded area.
    
    Args:
        bg_img: Background image (can be 3D or 4D)
        exclusion_mask: Mask of excluded area
        seed_coords: Coordinates of seed
        seed_radius: Radius of seed in mm
        exclusion_radius: Radius of exclusion in mm
        outdir: Output directory
        seed_name: Name of seed
    """
    from nilearn import plotting, image
    import matplotlib.pyplot as plt
    import os
    
    # Convert 4D image to 3D if necessary
    if isinstance(bg_img, str):
        bg_img = load_img(bg_img)
    
    if len(bg_img.shape) == 4:
        # Extract the first volume (or mean) from the 4D image
        bg_img = image.index_img(bg_img, 0)  # Or use image.mean_img(bg_img)
    
    # Create a figure with a custom title
    fig = plt.figure(figsize=(12, 4))
    fig.suptitle(f"Controlling for spatial autocorrelation around {seed_name} seed", fontsize=16)
    
    # Create the display
    display = plotting.plot_roi(
        exclusion_mask,
        bg_img=bg_img,
        cut_coords=seed_coords[0],
        title=f"Excluded region (r={exclusion_radius}mm)",
        figure=fig
    )
    
    # Add markers for the seed with a different color and size indicating the seed radius
    display.add_markers(
        marker_coords=seed_coords,
        marker_color="g",
        marker_size=seed_radius * 2  # Scale marker to represent seed radius
    )
    
    # Add a text annotation explaining the visualization
    plt.figtext(
        0.5, 0.01,
        f"Green marker: Seed region (r={seed_radius}mm)\n"
        f"Red area: Excluded voxels (r={exclusion_radius}mm) to control for spatial autocorrelation",
        ha="center",
        fontsize=12
    )
    
    # Make sure the output directory exists
    os.makedirs(outdir, exist_ok=True)
    
    # Save the figure
    output_file = f"{outdir}/spatial_autocorrelation_control_{seed_name}.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Saved spatial autocorrelation control visualization to {output_file}")
    
    return output_file

def main():
    print("Running resting state analysis...")
    subj_id = "s1273"
    sub_dir = get_sub_dir(subj_id)
    session_dirs = get_session_dirs(sub_dir)
    session_dirs.sort()

    # Seed location and name
    seed_coords = [(0, -52, 18)]
    seed_name = "PCC"
    seed_radius = 8  # mm, for extracting seed time series
    exclusion_radius = 30  # mm, for masking surrounding voxels (slightly larger)

    for ses_dir in session_dirs:
        ses_id = os.path.basename(ses_dir)
        print(f"Processing {subj_id} - {ses_id}")

        bold, confound, mask = get_files(ses_dir)

        # Prepare output directory for figs
        outdir = f"results/{subj_id}/{ses_id}"
        os.makedirs(outdir, exist_ok=True)

        # Step 1: Create a sphere mask for the area we want to exclude
        exclusion_sphere_file = create_sphere_mask(
            coords=seed_coords[0],
            radius_mm=exclusion_radius,
            mask_img=mask,
            output_file=f"{outdir}/exclusion_sphere_{seed_name}.nii.gz"
        )

        # Step 2: Create a mask that excludes the voxels in this sphere
        analysis_mask_file = create_exclusion_mask(
            mask_img=mask,
            sphere_mask_img=exclusion_sphere_file,
            output_file=f"{outdir}/analysis_mask_{seed_name}.nii.gz"
        )

        # Step 3: Extract the seed time series (same for both analyses)
        seed_masker = NiftiSpheresMasker(
            seed_coords,
            mask_img=mask,  # Use full brain mask for seed
            radius=seed_radius,
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
        
        print(f"Seed time series shape: ({seed_time_series.shape})")
        
        # Plot seed time series
        plot_seed_time_series(seed_time_series, outdir, seed_name)

        #------------------------------------------------
        # ANALYSIS 1: Standard approach (with all voxels)
        #------------------------------------------------
        print("\n=== Running standard analysis (with all voxels) ===")
        
        # Extract brain time series using full brain mask
        brain_masker_standard = NiftiMasker(
            mask_img=mask,  # Use standard brain mask
            smoothing_fwhm=6,
            detrend=True,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            t_r=1.49,
            memory="nilearn_cache",
            memory_level=1,
            verbose=0,
        )

        brain_time_series_standard = brain_masker_standard.fit_transform(
            bold, confounds=[confound]
        )
        
        print(f"Brain time series shape (standard): ({brain_time_series_standard.shape})")
        
        # Calculate correlations between seed and all brain voxels
        seed_to_voxel_correlations_standard = (
            np.dot(brain_time_series_standard.T, seed_time_series) / seed_time_series.shape[0]
        )
        
        print(
            "Seed-to-voxel correlation (standard): "
            f"min = {seed_to_voxel_correlations_standard.min():.3f}; "
            f"max = {seed_to_voxel_correlations_standard.max():.3f}"
        )
        
        # Transform correlations back to brain space
        seed_to_voxel_correlations_img_standard = brain_masker_standard.inverse_transform(
            seed_to_voxel_correlations_standard.T
        )
        
        # Visualize standard correlation map
        plot_seed_to_voxel_correlation(
            seed_to_voxel_correlations_img_standard,
            outdir,
            seed_coords,
            threshold=0.5,
            outfile=f"seed_correlation_standard_{seed_name}.pdf",
            title=f"Standard seed-to-voxel correlation\n(including all voxels)"
        )
        
        # Save standard analysis metadata
        metadata_standard = add_metadata(
            seed_time_series,
            brain_time_series_standard,
            seed_to_voxel_correlations_standard,
            seed_coords,
            seed_name
        )
        metadata_standard["analysis_type"] = "standard"
        dump_json(metadata_standard, f"{outdir}/meta_standard")

        #------------------------------------------------
        # ANALYSIS 2: Controlling for spatial autocorrelation
        #------------------------------------------------
        print("\n=== Running analysis with spatial autocorrelation control ===")
        
        # Extract brain time series, excluding the sphere around the seed
        brain_masker_excluded = NiftiMasker(
            mask_img=analysis_mask_file,  # Use the mask that excludes the sphere
            smoothing_fwhm=6,
            detrend=True,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            t_r=1.49,
            memory="nilearn_cache",
            memory_level=1,
            verbose=0,
        )

        brain_time_series_excluded = brain_masker_excluded.fit_transform(
            bold, confounds=[confound]
        )
        
        print(f"Brain time series shape (excluded): ({brain_time_series_excluded.shape})")
        
        # Calculate correlations with voxels around seed excluded
        seed_to_voxel_correlations_excluded = (
            np.dot(brain_time_series_excluded.T, seed_time_series) / seed_time_series.shape[0]
        )
        
        print(
            "Seed-to-voxel correlation (excluded): "
            f"min = {seed_to_voxel_correlations_excluded.min():.3f}; "
            f"max = {seed_to_voxel_correlations_excluded.max():.3f}"
        )
        
        # Transform correlations back to brain space
        seed_to_voxel_correlations_img_excluded = brain_masker_excluded.inverse_transform(
            seed_to_voxel_correlations_excluded.T
        )
        
        # Visualize correlation map with exclusion
        plot_seed_to_voxel_correlation(
            seed_to_voxel_correlations_img_excluded,
            outdir,
            seed_coords,
            threshold=0.5,
            outfile=f"seed_correlation_excluded_{seed_name}.pdf",
            title=f"Seed-to-voxel correlation\n(excluding {exclusion_radius}mm around seed)"
        )
        
        # Save excluded analysis metadata
        metadata_excluded = add_metadata(
            seed_time_series,
            brain_time_series_excluded,
            seed_to_voxel_correlations_excluded,
            seed_coords,
            seed_name
        )
        metadata_excluded.update({
            "analysis_type": "spatial_autocorrelation_controlled",
            "seed_radius_mm": seed_radius,
            "exclusion_radius_mm": exclusion_radius,
            "exclusion_sphere_file": exclusion_sphere_file,
            "analysis_mask_file": analysis_mask_file
        })
        dump_json(metadata_excluded, f"{outdir}/meta_excluded")

        #------------------------------------------------
        # Create comparison visualizations
        #------------------------------------------------
        
        # Create visualization showing the seed and excluded area
        create_visualization_with_exclusion(
            bold,
            exclusion_sphere_file,
            seed_coords,
            seed_radius,
            exclusion_radius,
            outdir,
            seed_name
        )
        
        # Create side-by-side comparison of the two correlation maps
        create_correlation_comparison(
            seed_to_voxel_correlations_img_standard,
            seed_to_voxel_correlations_img_excluded,
            seed_coords,
            exclusion_radius,
            outdir,
            seed_name,
            threshold=0.5,
            create_masked_version=True  # This creates a manually masked version
        )
        
        break  # Process only the first session

# Helper function to create side-by-side comparison
def create_correlation_comparison(
    standard_img, 
    excluded_img, 
    seed_coords, 
    exclusion_radius, 
    outdir, 
    seed_name,
    threshold=0.5,
    create_masked_version=True
):
    """
    Create a side-by-side comparison of standard and spatial-autocorrelation-controlled correlation maps.
    
    Args:
        standard_img: Standard correlation map
        excluded_img: Correlation map with excluded voxels
        seed_coords: Coordinates of seed
        exclusion_radius: Radius of exclusion in mm
        outdir: Output directory
        seed_name: Name of seed
        threshold: Threshold for correlation visualization
        create_masked_version: Whether to create a manually masked version
    """
    import matplotlib.pyplot as plt
    from nilearn import plotting, image
    import os
    import numpy as np
    
    # If requested, create a manually masked version of the standard image
    if create_masked_version:
        # Load the sphere mask to get excluded region
        if os.path.exists(f"{outdir}/exclusion_sphere_{seed_name}.nii.gz"):
            sphere_mask = load_img(f"{outdir}/exclusion_sphere_{seed_name}.nii.gz")
            
            # Get data from sphere mask and standard image
            sphere_data = image.get_data(sphere_mask).astype(bool)
            std_img_data = image.get_data(standard_img)
            
            # Create a copy of standard image data
            masked_data = std_img_data.copy()
            
            # Zero out the values inside the sphere mask
            masked_data[sphere_data] = 0
            
            # Create a new image with masked data but same metadata
            masked_img = image.new_img_like(standard_img, masked_data)
        else:
            print(f"Warning: Couldn't find sphere mask at {outdir}/exclusion_sphere_{seed_name}.nii.gz")
            masked_img = excluded_img  # Fallback to excluded_img if sphere mask not found
    else:
        masked_img = excluded_img  # Use the excluded image as provided
    
    # Get absolute maximum value from both images for a symmetric colorbar
    std_data = np.abs(image.get_data(standard_img))
    masked_data = np.abs(image.get_data(masked_img))
    
    # Find the maximum value across both images (ignoring zeros and NaNs)
    std_max = np.max(std_data[std_data > 0]) if np.any(std_data > 0) else 0
    masked_max = np.max(masked_data[masked_data > 0]) if np.any(masked_data > 0) else 0
    
    # Use the max value from both, capped for better visualization
    vmax = min(max(std_max, masked_max), 0.8)  # Cap at 0.8 (or adjust as needed)
    
    # Create a figure with multiple axes
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f"Effect of controlling for spatial autocorrelation - {seed_name} seed", fontsize=16)
    
    # Plot standard correlation map
    display1 = plotting.plot_stat_map(
        standard_img,
        threshold=threshold,
        cut_coords=seed_coords[0],
        title="Standard analysis\n(all voxels included)",
        axes=axes[0],
        colorbar=True,
        vmax=vmax,
        symmetric_cbar=True  # This ensures -vmax to +vmax range
    )
    
    # Plot masked correlation map
    display2 = plotting.plot_stat_map(
        masked_img,
        threshold=threshold,
        cut_coords=seed_coords[0],
        title=f"Controlled for spatial autocorrelation\n(excluded {exclusion_radius}mm around seed)",
        axes=axes[1],
        colorbar=True,
        vmax=vmax,
        symmetric_cbar=True  # This ensures -vmax to +vmax range
    )
    
    # Add markers for the seed
    display1.add_markers(marker_coords=seed_coords, marker_color="g", marker_size=10)
    display2.add_markers(marker_coords=seed_coords, marker_color="g", marker_size=10)
    
    # Add annotation explaining the visualization and colorbar scaling
    plt.figtext(
        0.5, 0.01,
        f"Green marker: Seed location at {seed_coords[0]}. Both panels use the same color scale (±{vmax:.2f}).",
        ha="center", fontsize=12
    )
    
    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)
    
    # Save the figure
    output_file = f"{outdir}/correlation_comparison_{seed_name}.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    print(f"Saved correlation comparison to {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()

