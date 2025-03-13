#TODO: get rid of duration_choice

#!/usr/bin/env python
import glob
import numpy as np
import pandas as pd
import json
import sys
import os
import nibabel as nb
from argparse import ArgumentParser, RawTextHelpFormatter
from utils_lev1.qa import qa_design_matrix, add_to_html_summary, get_all_contrast_vif, create_fixed_effects_html

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
    
    """
    Use the code below only for the discovery sample, not the validation sample. 

    The code below is used to address an issue with the nback blocked design in the discovery sample. 

    # if task == 'nBack':
    #     confounds = confounds_df.filter(regex='cosine0[0-4]'
    #                                 '|trans_x$|trans_x_derivative1$|trans_x_power2$|trans_x_derivative1_power2$'
    #                                 '|trans_y$|trans_y_derivative1$|trans_y_power2$|trans_y_derivative1_power2$'
    #                                 '|trans_z$|trans_z_derivative1$|trans_z_power2$|trans_z_derivative1_power2$'
    #                                 '|rot_x$|rot_x_derivative1$|rot_x_power2$|rot_x_derivative1_power2$'
    #                                 '|rot_y$|rot_y_derivative1$|rot_y_power2$|rot_y_derivative1_power2$'
    #                                 '|rot_z$|rot_z_derivative1$|rot_z_power2$|rot_z_derivative1_power2$')
    # else:
    # confounds = confounds_df.filter(
    #     regex='cosine'
    #     '|trans_x$|trans_x_derivative1$|trans_x_power2$|trans_x_derivative1_power2$'
    #     '|trans_y$|trans_y_derivative1$|trans_y_power2$|trans_y_derivative1_power2$'
    #     '|trans_z$|trans_z_derivative1$|trans_z_power2$|trans_z_derivative1_power2$'
    #     '|rot_x$|rot_x_derivative1$|rot_x_power2$|rot_x_derivative1_power2$'
    #     '|rot_y$|rot_y_derivative1$|rot_y_power2$|rot_y_derivative1_power2$'
    #     '|rot_z$|rot_z_derivative1$|rot_z_power2$|rot_z_derivative1_power2$'
    # )

    """

    confounds = confounds_df.filter(
        regex='cosine|trans_x$|trans_x_derivative1$|trans_x_power2$|trans_x_derivative1_power2$'
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
    mean_rt,
    confounds_file=None,
    regress_rt="no_rt",
    model_break=False
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
    from utils_lev1.first_level_designs_new_event_files import make_task_desmat_fcn_dict

    if confounds_file is not None:
        confound_regressors = get_confounds_tedana(confounds_file, task)
    else:
        confound_regressors = None

    tr = 1.49
    print('model_break: ', model_break)
    design_matrix, contrasts, percent_junk, simplified_events_df = make_task_desmat_fcn_dict[task](
        events_file,
        duration_choice,
        add_deriv,
        regress_rt,
        mean_rt,
        n_scans,
        tr,
        confound_regressors,
        model_break
    )
    return design_matrix, contrasts, tr, percent_junk, simplified_events_df


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


def get_files(root, subid, task):
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
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*T1w*mask*.nii.gz")
    )

    files["data_file"] = sorted(
        glob.glob(f"{root}/sub-{subid}/ses-*/func/*{task}_*T1w*_desc-optcom_bold.nii.gz")
    )

    return files

def calculate_mean_rt(root, task):
    event_files = glob.glob(root+f'/*/*/func/*{task}_*events.tsv')
    mean_rts = []
    if 'stopSignal' in task:
        for event_file in event_files:
            df = pd.read_csv(event_file, sep='\t')
            df['trial_type'].fillna('n/a', inplace=True)
            subset = df.query("(trial_type.str.contains('go') and response_time >= 0.2 and key_press == correct_response)" +
                                "or (trial_type.str.contains('stop_failure') and response_time >= 0.2)", engine='python')
            mean_rt = subset['response_time'].mean()
            mean_rts.append(mean_rt)
    else:
        for event_file in event_files:
            df = pd.read_csv(event_file, sep='\t')
            subset = df.query("key_press == correct_response and trial_id == 'test_trial' and response_time >= 0.2")
            mean_rt = subset['response_time'].mean()
            mean_rts.append(mean_rt)
    
    return np.mean(mean_rts)

def get_parser():
    """Build parser object"""
    parser = ArgumentParser(
        prog="analyze_lev1",
        description="analyze_lev1: Runs level 1 analyses with or without RT confound",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "task",
        action="store",
        type=str,
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
        "--model_break",
        action="store_true",
        help=(
            "Use to specify whether to include a break regressor. This would affect implicit baseline"
        ),
    )
    # Add performance only feedback option --only_breaks_with_performance_feedback
    parser.add_argument(
        "--only_breaks_with_performance_feedback",
        action="store_true",
        help=(
            "Only model breaks with performance feedback"
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


def filter_files(files, subid, task):
    """
    Exclude certain task sessions for certain subjects and print removed files
    """

    exclude_dict = {
        "s1134": [("rest", "ses-07"), ("rest", "ses-10")],
        "s1174": [("rest", "ses-05")],
        "s1258": [("rest", "ses-07")],
        "s1391": [
            ("rest", "ses-02"),
            ("rest", "ses-03"),
            ("rest", "ses-04"),
            ("rest", "ses-08"),
            ("rest", "ses-09"),
            ("rest", "ses-10"),
            ("goNogo", "ses-07")
        ],
        "s1445": [("rest", "ses-05")],
        "s180": [("rest", "ses-06"), ("rest", "ses-07")],
        "s216": [("rest", "ses-05")],
        "s321": [
            ("flanker", "ses-07"),
            ("rest", "ses-08"),
            ("flanker", "ses-09"),
            ("nBackWShapeMatching", "ses-12")
        ],
        "s599": [("rest", "ses-02")]
    }

    if subid in exclude_dict:
        exclude_list = exclude_dict[subid]
        filtered_files = []
        removed_files = []
        for file in files:
            should_include = True
            for exclude_task, exclude_ses in exclude_list:
                if task == exclude_task and f"_{exclude_ses}_" in file:
                    should_include = False
                    removed_files.append(file)
                    break
            if should_include:
                filtered_files.append(file)
        
        print("Removed files:")
        for file in removed_files:
            print(file)
        
        return filtered_files
    else:
        print("No files removed.")
        return files

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
    model_break = opts.model_break
    only_breaks_with_performance_feedback = opts.only_breaks_with_performance_feedback
    print("Only model breaks with performance feedback: ",only_breaks_with_performance_feedback)

    if opts.omit_deriv:
        add_deriv = "deriv_no"
    else:
        add_deriv = "deriv_yes"
    duration_choice = "constant"

    # Paths for validation sample
    bids = "/oak/stanford/groups/russpold/data/network_grant/validation_BIDS"
    root = f"{bids}/derivatives/glm_data"

    if model_break:
        if only_breaks_with_performance_feedback:
            outdir = f"{bids}/derivatives/lev_1_output/{task}_lev1_model_break_performance_feedback_only"
        else:
            outdir = f"{bids}/derivatives/lev_1_output/{task}_lev1_model_break"
    else:
        outdir = f"{bids}/derivatives/lev_1_output/{task}_lev1_model"
    
    if add_deriv == "deriv_yes":
        outdir = f"{outdir}_deriv"
    else:
        outdir = f"{outdir}_no_deriv"

    contrast_dir = f"{outdir}/task_{task}_rtmodel_{regress_rt}"
 
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(f"{contrast_dir}/contrast_estimates", exist_ok=True)

    files = get_files(root=root, subid=subid, task=task)

    print("---- FILES BEFORE FILTERING ----")
    print(f"Total number of files: {len(files['data_file'])}")
    print(f"Total number of events files: {len(files['events_file'])}")
    print(f"Total number of confounds files: {len(files['confounds_file'])}")

    assert len(files['data_file']) == len(files['events_file']) == len(files['confounds_file']), \
        f"Mismatch in file counts: data_files({len(files['data_file'])}), events_files({len(files['events_file'])}), confounds_files({len(files['confounds_file'])})"

    # Apply filtering
    files['data_file'] = filter_files(files['data_file'], subid, task)
    files['events_file'] = filter_files(files['events_file'], subid, task)
    files['confounds_file'] = filter_files(files['confounds_file'], subid, task)

    print(files['data_file'])
    print("---- FILES AFTER FILTERING ----")
    print(f"Total number of files: {len(files['data_file'])}")
    print(f"Total number of events files: {len(files['events_file'])}")
    print(f"Total number of confounds files: {len(files['confounds_file'])}")

    effect_size_files = {}
    variance_files = {}
    mean_rt = calculate_mean_rt(root, task)

    for data_file in files["data_file"]:
        ses = data_file.split("/")[-3]
        event_file = [i for i in files["events_file"] if ses in i][0]
        confounds_file = [i for i in files["confounds_file"] if ses in i][0]
        mask_file = [i for i in files["mask_file"] if ses in i][0]
        n_scans = get_nscans(data_file)
  
        design_matrix, contrasts, tr, percent_junk, simplified_events_df = make_desmat_contrasts(
            root,
            task,
            event_file,
            duration_choice,
            add_deriv,
            n_scans,
            mean_rt,
            confounds_file,
            regress_rt,
            model_break
        )
        design_matrix['constant'] = 1
        if simplified_events:
            if not os.path.exists(f"{contrast_dir}/simplified_events"):
                os.makedirs(f"{contrast_dir}/simplified_events")
            simplified_filename = f"{contrast_dir}/simplified_events/sub-{subid}_{ses}_task-{task}_simplified-events.csv"
            simplified_events_df.to_csv(simplified_filename)

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
            model_break,
            add_deriv,
            only_breaks_with_performance_feedback 
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
        # Save out fixed effects contrasts to separate directory
        fixed_effects_dir = f'{contrast_dir}/contrast_estimates'.replace('lev_1_output', 'within_subject_fixed_effects')
        os.makedirs(fixed_effects_dir, exist_ok=True)

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
                effect_size_files, variance_files, precision_weighted=False
            )
            fixed_effects_filename = (
                f"{fixed_effects_dir}/sub-{subid}_task-{task}_contrast-{con_name}_rtmodel-{regress_rt}"
                + "_stat-fixed-effects_t-test.nii.gz"
            )
            fixed_fx_stat.to_filename(fixed_effects_filename)
            create_fixed_effects_html(fixed_effects_filename, fixed_fx_contrast, fixed_fx_variance, fixed_fx_stat)
            
    # -
