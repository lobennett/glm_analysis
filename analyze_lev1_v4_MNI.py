#!/usr/bin/env python
import glob
import numpy as np
import pandas as pd
import json
import sys
import os
import nibabel as nb
from argparse import ArgumentParser, RawTextHelpFormatter
from utils_lev1.qa import qa_design_matrix, add_to_html_summary, get_all_contrast_vif


def get_confounds_tedana(confounds_file, task):
    """
    Creates nuisance regressors from fmriprep confounds timeseries.
    input:
      confounds_file: path to confounds file from fmriprep
    output:
      confound_regressors: includes aCompCor, FD, 6 motion regressors + derivatives,
                            cosine basis set (req with compcor use)
    """
    confounds_df = pd.read_csv(confounds_file, sep="\t", na_values=["n/a"]).fillna(0)

    confounds = confounds_df.filter(
        regex='cosine'
        '|trans_x$|trans_x_derivative1$|trans_x_power2$|trans_x_derivative1_power2$'
        '|trans_y$|trans_y_derivative1$|trans_y_power2$|trans_y_derivative1_power2$'
        '|trans_z$|trans_z_derivative1$|trans_z_power2$|trans_z_derivative1_power2$'
        '|rot_x$|rot_x_derivative1$|rot_x_power2$|rot_x_derivative1_power2$'
        '|rot_y$|rot_y_derivative1$|rot_y_power2$|rot_y_derivative1_power2$'
        '|rot_z$|rot_z_derivative1$|rot_z_power2$|rot_z_derivative1_power2$'
    )
    confounds = confounds.reset_index(drop=True)

    return confounds


def get_nscans(timeseries_data_file):
    """
    Get the number of time points from 4D data file
    input: time_series_data_file: Path to 4D file
    output: nscans: number of time points
    """

    fmri_data = nb.load(timeseries_data_file)
    n_scans = fmri_data.shape[3]
    return n_scans


def get_tr(root, task):
    """
    Get the TR from the bold json file
    input:
        root: Root for BIDS data directory
        task: Task name
    output: TR as reported in json file (presumable in s)
    """
    json_file = glob.glob(f"{root}/sub-*/ses-*/*{task}_bold.json")[0]
    with open(json_file, "rb") as f:
        task_info = json.load(f)
    tr = task_info["RepetitionTime"]
    return tr


def make_desmat_contrasts(
    root,
    task,
    events_file,
    duration_choice,
    add_deriv,
    n_scans,
    confounds_file=None,
    regress_rt="no_rt",
):
    """
    Creates design matrices and contrasts for each task.  Should work for any
    style of design matrix as well as the regressors are defined within
    the imported make_task_desmat_fcn_map (dictionary of functions).
    A single RT regressor can be added using regress_rt='rt_uncentered'
    Input:
        root:  Root directory (for BIDS data)
        task: Task name
        events_file: File path to events.tsv for the given task
        duration_choice: used for duration in regressors
        add_deriv: 'deriv_yes' or 'deriv_no', recommended to use 'deriv_yes'
        n_scans: Number of scans
        confound_file (optional): File path to fmriprep confounds file
        regress_rt: 'no_rt' or 'rt_uncentered' or 'rt_centered'
    Output:
        design_matrix, contrasts: Full design matrix and contrasts for nilearn model
        percent junk: percentage of trials labeled as "junk".  Used in later QA.
        percent high motion: percentage of time points that are high motion.  Used later in QA.
    """
    from utils_lev1.first_level_designs import make_task_desmat_fcn_dict

    if confounds_file is not None:
        confound_regressors = get_confounds_tedana(confounds_file, task)
    else:
        confound_regressors = None

    tr = 1.49

    design_matrix, contrasts, percent_junk, events_df = make_task_desmat_fcn_dict[task](
        events_file,
        duration_choice,
        add_deriv,
        regress_rt,
        n_scans,
        tr,
        confound_regressors,
    )
    return design_matrix, contrasts, tr, percent_junk, events_df


def check_file(glob_out, task):
    """
    Checks if file exists
    input:
        glob_out: output from glob call attempting to retreive files.  Note this
        might be simplified for other data.  Since the tasks differed between sessions
        across subjects, the ses directory couldn't be hard coded, in which case glob
        would not be necessary.
    output:
        file: Path to file, if it exists
        file_missing: Indicator for whether or not file exists (used in later QA)
    """
    if task in [
        "cuedTS",
        "directedForgetting",
        "flanker",
        "goNogo",
        "nBack",
        "stopSignal",
        "spatialTS",
        "shapeMatching",
    ]:
        if len(glob_out) >= 5:
            file = glob_out
            file_missing = [0]
        else:
            file = glob_out
            file_missing = [1]
    else:
        if len(glob_out) >= 2:
            file = glob_out
            file_missing = [0]
        else:
            file = glob_out
            file_missing = [1]
    return file, file_missing


def get_files(root, tedana_root, subid, task):
    """Fetches files (events.tsv, confounds, mask, data)
    if files are not present, excluded_subjects.csv is updated and
    program exits
    input:
        root:  Root directory
        subid: subject ID (without s prefix)
        task: Task
    output:
       files: Dictionary with file paths (or empty lists).  Needs to be further
           processed by check_file() to pick up instances when task is not available
           for a given subject (missing data files)
           Dictionary contains events_file, mask_file, confounds_file, data_file
    """
    files = {}

    files["events_file"] = sorted(
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*events*tsv")
    )

    files["confounds_file"] = sorted(
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*confounds*.tsv")
    )

    files["mask_file"] = sorted(
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*MNI*mask*.nii.gz")
    )

    files["data_file"] = sorted(
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*MNI*_desc-optcom_bold.nii.gz")
    )

    print(files)
    return files


def get_parser():
    """Build parser object"""
    parser = ArgumentParser(
        prog="analyze_lev1",
        description="analyze_lev1: Runs level 1 analyses with or without RT confound",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "task",
        choices=[
            "cuedTS",
            "directedForgetting",
            "flanker",
            "goNogo",
            "nBack",
            "stopSignal",
            "spatialTS",
            "shapeMatching",
            "stopSignalWDirectedForgetting",
            "stopSignalWFlanker",
            "directedForgettingWFlanker",
        ],
        help="Use to specify task.",
    )
    parser.add_argument(
        "subid",
        action="store",
        type=str,
        help="String indicating subject id",
    )
    parser.add_argument(
        "regress_rt",
        choices=["no_rt", "rt_uncentered", "rt_centered"],
        help=(
            "Use to specify how rt is/is not modeled. If rt_centered is used "
            "you will potentially have an RT confound in the group models"
        ),
    )
    parser.add_argument(
        "--omit_deriv",
        action="store_true",
        help=(
            "Use to omit derivatives for task-related regressors "
            "(typically you would want derivatives)"
        ),
    )
    parser.add_argument(
        "--qa_only",
        action="store_true",
        help=(
            "Use this flag if you only want to QA model setup without estimating model."
        ),
    )
    parser.add_argument(
        "--fixed_effects",
        action="store_true",
        help=(
            "Use this flag to run fixed effects analysis within subject across sessions."
        ),
    )
    parser.add_argument(
        "--simplified_events",
        action="store_true",
        help=("Use this flag to create simplified events"),
    )
    parser.add_argument(
        "--residuals",
        action="store_true",
        help=("Use this flag to create residual images"),
    )
    return parser


if __name__ == "__main__":
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn.glm.contrasts import compute_fixed_effects

    opts = get_parser().parse_args(sys.argv[1:])
    qa_only = opts.qa_only
    subid = opts.subid
    regress_rt = opts.regress_rt
    task = opts.task
    fixed_effects = opts.fixed_effects
    simplified_events = opts.simplified_events
    residuals = opts.residuals

    if opts.omit_deriv:
        add_deriv = "deriv_no"
    else:
        add_deriv = "deriv_yes"
    duration_choice = "constant"

    bids = '/oak/stanford/groups/russpold/data/network_grant/validation_BIDS'
    root = f'{bids}/derivatives/glm_data'
    outdir = f'{bids}/derivatives/output_v4_MNI/{task}_lev1_output'
    tedana_root = f'{bids}/derivatives/tedana_kundu'
    contrast_dir = f"{outdir}/task_{task}_rtmodel_{regress_rt}"
    
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(f"{contrast_dir}/contrast_estimates", exist_ok=True)

    files = get_files(root, tedana_root, subid, task)

    total_num_files = len(files["data_file"])

    print(f"Total number of files: {total_num_files}")
    print(f"Total number of events files: {len(files['events_file'])}")
    print(f"Total number of confounds files: {len(files['confounds_file'])}")

    assert (
        len(files["events_file"])
        == total_num_files & len(files["confounds_file"])
        == total_num_files
    )
    
    effect_size_files = {}
    variance_files = {}

    for data_file in files["data_file"]:
        ses = data_file.split("/")[-3]
        event_file = [i for i in files["events_file"] if ses in i][0]
        confounds_file = [i for i in files["confounds_file"] if ses in i][0]
        mask_file = [i for i in files["mask_file"] if ses in i][0]
        n_scans = get_nscans(data_file)
        design_matrix, contrasts, tr, percent_junk, events_df = make_desmat_contrasts(
            root,
            task,
            event_file,
            duration_choice,
            add_deriv,
            n_scans,
            confounds_file,
            regress_rt,
        )
        design_matrix['constant'] = 1
        if simplified_events:
            if not os.path.exists(f"{contrast_dir}/simplified_events"):
                os.makedirs(f"{contrast_dir}/simplified_events")
            simplified_filename = f"{contrast_dir}/simplified_events/sub-{subid}_{ses}_task-{task}_simplified-events.csv"
            events_df.to_csv(simplified_filename)

        exclusion, any_fail = qa_design_matrix(
            contrast_dir,
            contrasts,
            design_matrix,
            subid,
            task,
            ses,
            percent_junk=percent_junk,
        )

        add_to_html_summary(
            subid,
            contrasts,
            design_matrix,
            contrast_dir,
            regress_rt,
            duration_choice,
            task,
            any_fail,
            exclusion,
            ses,
            percent_junk,
        )

        if not any_fail and qa_only == False:
            print(f"Running model for {data_file}")
            if not residuals:
                fmri_glm = FirstLevelModel(
                    tr,
                    subject_label=subid,
                    mask_img=mask_file,
                    noise_model="ar1",
                    standardize=False,
                    drift_model=None,
                    smoothing_fwhm=5,
                    minimize_memory=True,
                )

                out = fmri_glm.fit(data_file, design_matrices=design_matrix)

                contrast_names = []
                for con_name, con in contrasts.items():
                    con_est = out.compute_contrast(con, output_type="all")
                    contrast_names.append(con_name)
                    effect_size_filename = (
                        f"{contrast_dir}/contrast_estimates/sub-{subid}_{ses}_task-{task}_contrast-{con_name}"
                        f"_rtmodel-{regress_rt}_stat"
                        f"-effect-size.nii.gz"
                    )
                    con_est["effect_size"].to_filename(effect_size_filename)
                    variance_filename = (
                        f"{contrast_dir}/contrast_estimates/sub-{subid}_{ses}_task-{task}_contrast-{con_name}"
                        f"_rtmodel-{regress_rt}_stat"
                        f"-variance.nii.gz"
                    )
                    con_est["effect_variance"].to_filename(variance_filename)
                    zscore_filename = (
                        f"{contrast_dir}/contrast_estimates/sub-{subid}_{ses}_task-{task}_contrast-{con_name}"
                        f"_rtmodel-{regress_rt}_stat"
                        f"-z_score.nii.gz"
                    )
                    con_est["z_score"].to_filename(zscore_filename)
                print(f"Contrast names: {contrast_names}")
                contrast_names.remove("task-baseline")

            # saving residuals for Mahalanobis distance analysis
            if residuals:
                fmri_glm = FirstLevelModel(
                    tr,
                    subject_label=subid,
                    mask_img=mask_file,
                    noise_model="ar1",
                    standardize=False,
                    drift_model=None,
                    smoothing_fwhm=5,
                    minimize_memory=False,
                )
                out = fmri_glm.fit(data_file, design_matrices=design_matrix)

                residuals_filename = f"{contrast_dir}/contrast_estimates/sub-{subid}_{ses}_task-{task}_rtmodel-{regress_rt}_residuals.nii.gz"
                fmri_glm.residuals[0].to_filename(residuals_filename)

    if fixed_effects:
        print('Contrasts: ', contrasts)
        for con_name, con in contrasts.items():
            effect_size_files = sorted(
                glob.glob(
                    f"{contrast_dir}/contrast_estimates/sub-{subid}_*contrast-{con_name}*effect-size.nii.gz"
                )
            )
            variance_files = sorted(
                glob.glob(
                    f"{contrast_dir}/contrast_estimates/sub-{subid}_*contrast-{con_name}*variance.nii.gz"
                )
            )
            fixed_fx_contrast, fixed_fx_variance, fixed_fx_stat = compute_fixed_effects(
                effect_size_files, variance_files, precision_weighted=True
            )
            fixed_effects_filename = (
                f"{contrast_dir}/contrast_estimates/sub-{subid}_task-{task}_contrast-{con_name}_rtmodel-{regress_rt}"
                + "_stat-fixed-effects_t-test.nii.gz"
            )
            fixed_contrast_filename = fixed_effects_filename.replace('_t-test.nii.gz', '_effect.nii.gz')
            fixed_fx_stat.to_filename(fixed_effects_filename)
            fixed_fx_contrast.to_filename(fixed_contrast_filename)
    # -
