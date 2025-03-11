from pathlib import Path

import numpy as np
import pandas as pd
from nilearn.glm.contrasts import compute_fixed_effects
from nilearn.glm.first_level import (
    FirstLevelModel,
    compute_regressor,
)
from nilearn.image import load_img

from network_glm.config import regressor_config, contrasts_config
from network_glm.quality_control import get_all_contrast_vif

def calculate_mean_rt(files: dict):
    mean_rts = []
    for session in files:
        # Read the events file once and store in df
        df = pd.read_csv(files[session]["events"], sep='\t')
        subset = df.query(
            "key_press == correct_response and trial_id == 'test_trial' "
            "and response_time >= 0.2"
        )
        mean_rt = subset['response_time'].mean()
        mean_rts.append(mean_rt)
    return np.mean(mean_rts)

def get_nscans(datafile: Path):
    return load_img(datafile).shape[3]

def get_files(subj_dir: Path, task_name: str, expected_file_count: int = 4):
    # The reason expected_file_count is 4 is because
    # - there are 4 files for each session:
    # - events.tsv
    # - optcom_bold.nii.gz
    # - confounds_timeseries.tsv
    # - brain_mask.nii.gz
    files = {}

    for file in sorted(
        subj_dir.glob(f"ses-*/*{task_name}*"),
        key=lambda x: x.parts[-2]
    ):
        session_name = file.parts[-2]

        if session_name not in files:
            files[session_name] = {}

        file_name = file.name
        if file_name.endswith("events.tsv"):
            files[session_name]["events"] = file
        elif file_name.endswith("desc-optcom_bold.nii.gz"):
            files[session_name]["data"] = file
        elif file_name.endswith("desc-confounds_timeseries.tsv"):
            files[session_name]["confounds"] = file
        elif file_name.endswith("desc-brain_mask.nii.gz"):
            files[session_name]["brain_mask"] = file

    for key in files:
        assert len(files[key]) == expected_file_count

    return files


def get_confounds_tedana(confounds_file: Path):
    confounds_df = pd.read_csv(confounds_file, sep="\t", na_values=["n/a"]).fillna(0)
    confounds = confounds_df.filter(
        regex='cosine|trans_x$|trans_x_derivative1$|trans_x_power2$|'
        'trans_x_derivative1_power2$|trans_y$|trans_y_derivative1$|trans_y_power2$|'
        'trans_y_derivative1_power2$|trans_z$|trans_z_derivative1$|trans_z_power2$|'
        'trans_z_derivative1_power2$|rot_x$|rot_x_derivative1$|rot_x_power2$|'
        'rot_x_derivative1_power2$|rot_y$|rot_y_derivative1$|rot_y_power2$|'
        'rot_y_derivative1_power2$|rot_z$|rot_z_derivative1$|rot_z_power2$|'
        'rot_z_derivative1_power2$'
    )
    return confounds.reset_index(drop=True)


def define_nuisance_trials(events_df: pd.DataFrame):
    # - consider trial an omission if did not press a key
    omission = ((events_df.key_press == -1) & (events_df.trial_id == "test_trial"))
    # - consider trial a commission if pressed the wrong key and rt > .2s
    commission = (
        (events_df.key_press != events_df.correct_response)
        & (events_df.key_press != -1)
        & (events_df.response_time >= 0.2)
        & (events_df.trial_id == "test_trial")
    )
    # - consider trial too fast if rt < .2s
    rt_too_fast = (
        (events_df.response_time < 0.2) &
        (events_df.trial_id == "test_trial")
    )
    # - consider trial 'bad' if it is any one of the above is true
    bad_trials = omission | commission | rt_too_fast

    return 1 * bad_trials, 1 * omission, 1 * commission, 1 * rt_too_fast


def make_regressor_and_derivative(
    n_scans,
    tr,
    events_df,
    add_deriv = False,
    amplitude_column=None,
    duration_column=None,
    onset_column="onset",
    subset=None,
    demean_amp=False,
    cond_id="cond",
):
    # THROW ERRORS IF MISSING COLUMNS
    if amplitude_column is None or duration_column is None:
        raise ValueError("Must enter amplitude and duration columns")
    if amplitude_column not in events_df.columns:
        raise ValueError("must specify amplitude column that exists in events_df")
    if duration_column not in events_df.columns:
        raise ValueError("must specify duration column that exists in events_df")

    reg_3col = events_df.query(subset)[
        [onset_column, duration_column, amplitude_column]
    ]
    reg_3col = reg_3col.rename(
        columns={duration_column: "duration", amplitude_column: "modulation"}
    )

    if demean_amp:
        reg_3col["modulation"] = reg_3col["modulation"] - reg_3col["modulation"].mean()

    if add_deriv:
        hrf_model = "spm + derivative"
    else:
        hrf_model = "spm"

    regressor_array, regressor_names = compute_regressor(
        np.transpose(np.array(reg_3col)),
        hrf_model,
        # deals with slice timing issue with outputs from fMRIPrep
        np.arange(n_scans) * tr + tr / 2,
        con_id=cond_id,
    )
    regressors = pd.DataFrame(regressor_array, columns=regressor_names)
    return regressors, reg_3col


def rename_columns(df, prefix):
    """
    Rename columns in a DataFrame by adding a prefix, preserving the onset/button_onset
    column name.

    Args:
        df (pd.DataFrame): Input DataFrame
        prefix (str): Prefix to add to column names

    Returns:
        pd.DataFrame: DataFrame with renamed columns
    """
    onset_column = 'onset' if 'onset' in df.columns else 'button_onset'
    renamed_columns = {col: f"{prefix}_{col}" for col in df.columns
                      if col != onset_column}
    return df.rename(columns=renamed_columns)

def create_simplified_events_df(dfs):
    """
    Merge multiple DataFrames on their onset column,
    adding prefixes to avoid column name conflicts.

    Args:
        dfs (list): List of tuples containing (DataFrame, prefix) pairs

    Returns:
        pd.DataFrame: Merged DataFrame containing all events
    """
    if not dfs:
        return pd.DataFrame()

    # Start with first DataFrame
    base_df = rename_columns(dfs[0][0], dfs[0][1])

    # Merge remaining DataFrames
    for df, prefix in dfs[1:]:
        df = rename_columns(df, prefix)
        base_df = base_df.merge(df, on='onset', how='outer')

    return base_df.sort_values('onset').reset_index(drop=True)

def create_regressors_from_config(config, events_df, nscans, tr, task_name=None):
    """
    Create regressors based on configuration dictionary

    Args:
        config (dict): Dictionary with regressor configurations
        events_df (pd.DataFrame): Events dataframe
        nscans (int): Number of scans
        tr (float): Repetition time
        task_name (str, optional): Task name to extract task-specific regressors

    Returns:
        tuple: (dict of regressors, list of (3col_df, name) tuples)
    """
    regressors = {}
    regressor_3cols = []

    if not task_name:
        raise ValueError("Task name is required")

    if task_name not in config:
        raise ValueError(f"Task name {task_name} not found in config")

    # Only process task-specific regressors if task_name exists in config
    for name, params in config[task_name].items():
        reg, reg_3col = make_regressor_and_derivative(
            n_scans=nscans,
            tr=tr,
            events_df=events_df,
            add_deriv=params.get('add_deriv', False),
            amplitude_column=params['amplitude_column'],
            duration_column=params['duration_column'],
            subset=params['subset'],
            demean_amp=params.get('demean_amp', False),
            cond_id=name,
        )
        regressors[name] = reg
        regressor_3cols.append((reg_3col, name))

    return regressors, regressor_3cols

def prepare_results_dir(results_dir: Path = Path("./results/")):
    subdirs = [
        "quality_control",
        "indiv_contrasts",
        "fixed_effects",
        "simplified_events"
    ]
    paths = [results_dir] + [Path(results_dir, d) for d in subdirs]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tuple(paths)

def main():
    # Prepare results directory
    # - These directories will contain the
    # - output for each of the models and
    # - quality control files for each model
    _, quality_control_dir, indiv_contrasts_dir, fixed_effects_dir, \
        simplified_events_dir = prepare_results_dir()

    # Prepare data directory
    # - This directory contains the BIDS data
    # - The data is organized by subject and session
    # - The necessary files include the optcom bold files,
    # - the event files, the brain masks, and the confounds files
    bids_dir = Path("./data/test_data/")
    subj_id = "s1273"
    task_name = "cuedTS"
    subj_dir = Path(bids_dir, f'sub-{subj_id}')

    # Get files for the subject and task
    files = get_files(subj_dir, task_name)

    # Calculate mean RT
    # - This is used to center the RT regressor
    mean_rt = calculate_mean_rt(files)
    tr = 1.49000
    model_break = True

    print("Mean RT: ", mean_rt)

    for session in files:
        print(f'Processing session {session}')

        # Get files for the current session which
        # we are processing.
        events = files[session]["events"]
        data = files[session]["data"]
        confounds = files[session]["confounds"]
        brain_mask = files[session]["brain_mask"]

        # Get the number of timepoints in the current session
        # - this is used to create the regressors
        nscans = get_nscans(data)

        # TEDANA CONFOUNDS
        # - These are the confounds that are created by TEDANA / FMRIPREP
        # - These map onto motion parameters
        confound_regressors = get_confounds_tedana(confounds)

        # EVENTS
        # - These are the events corresponding to the task
        # - Here, we add the nuisance trials to the events dataframe
        events_df = pd.read_csv(events, sep="\t", dtype={'response_time': float})
        (
            events_df["junk_trials"],
            events_df["omission"],
            events_df["commission"],
            events_df["rt_fast"],
        ) = define_nuisance_trials(events_df)

        # TODO: Add to quality control
        # Remove unused variable or use it
        # percent_junk = np.mean(events_df["junk_trials"])

        # Add column containing all 1s
        events_df["constant_1_column"] = 1
        
        # Add response_time_centered column for RT regressor
        events_df["response_time_centered"] = events_df.response_time - mean_rt

        # Add break period if needed
        if model_break:
            regressor_config[task_name]["break_period"] = {
                "amplitude_column": "constant_1_column",
                "duration_column": "duration",
                "subset": 'trial_id == "break_with_performance_feedback"',
            }

        # Create regressors from config
        regressors_dict, regressor_dfs = create_regressors_from_config(
            regressor_config, events_df, nscans, tr, task_name
        )

        # Create design matrix
        design_matrix = pd.concat(
            [regressors_dict[name] for name in regressors_dict] + [confound_regressors],
            axis=1,
        )

        simplified_events_df = create_simplified_events_df(regressor_dfs)
        simplified_events_df.to_csv(
            f"{simplified_events_dir}/sub-{subj_id}_{session}_task-{task_name}_"
            f"simplified_events.csv",
            index=False
        )

        # Get contrasts from config for task
        contrasts = contrasts_config[task_name]
        design_matrix['constant'] = 1

        # Fit GLM to the data
        fmri_glm = FirstLevelModel(
            tr,
            subject_label=subj_id,
            mask_img=brain_mask,
            noise_model="ar1",
            standardize=False,
            drift_model=None,
            smoothing_fwhm=5,
            minimize_memory=True,
        )

        out = fmri_glm.fit(data, design_matrices=design_matrix)

        # Save the contrasts
        contrast_names = []
        for contrast_name, contrast_formula in contrasts.items():
            con_est = out.compute_contrast(contrast_formula, output_type="all")
            contrast_names.append(contrast_name)

            # Get effect size, variance, and z-score
            effect_size = con_est["effect_size"]
            variance = con_est["effect_variance"]
            z_score = con_est["z_score"]

            # Save to file
            effect_size.to_filename(
                f"{indiv_contrasts_dir}/sub-{subj_id}_{session}_task-{task_name}_"
                f"contrast-{contrast_name}_rtmodel-rt_centered_stat-effect-size.nii.gz"
            )
            variance.to_filename(
                f"{indiv_contrasts_dir}/sub-{subj_id}_{session}_task-{task_name}_"
                f"contrast-{contrast_name}_rtmodel-rt_centered_stat-variance.nii.gz"
            )
            z_score.to_filename(
                f"{indiv_contrasts_dir}/sub-{subj_id}_{session}_task-{task_name}_"
                f"contrast-{contrast_name}_rtmodel-rt_centered_stat-z_score.nii.gz"
            )

        # QUALITY CONTROL
        # - Save out VIFs for each contrast
        vif_contrasts = get_all_contrast_vif(design_matrix, contrasts)
        vif_contrasts.to_csv(
            f"{quality_control_dir}/sub-{subj_id}_{session}_task-{task_name}_"
            f"rtmodel-rt_centered_stat-vif_contrasts.csv",
            index=False
        )

    print("Contrasts: ", contrast_names)

    # Filter out task-baseline contrast for fixed effects model
    contrast_names = [c for c in contrast_names if c != "task-baseline"]

    # Save out fixed effects contrasts
    for contrast_name in contrast_names:
        print(f"Processing fixed effects contrast for {contrast_name}")
        effects_files = [
            f for f in indiv_contrasts_dir.glob(
                f"sub-{subj_id}_*_task-{task_name}_contrast-{contrast_name}_"
                f"rtmodel-rt_centered_stat-effect-size.nii.gz"
            )
        ]
        variances_files = [
            f for f in indiv_contrasts_dir.glob(
                f"sub-{subj_id}_*_task-{task_name}_contrast-{contrast_name}_"
                f"rtmodel-rt_centered_stat-variance.nii.gz"
            )
        ]
        z_scores_files = [
            f for f in indiv_contrasts_dir.glob(
                f"sub-{subj_id}_*_task-{task_name}_contrast-{contrast_name}_"
                f"rtmodel-rt_centered_stat-z_score.nii.gz"
            )
        ]

        assert len(effects_files) == len(variances_files) == len(z_scores_files)

        fixed_fx_contrast, fixed_fx_variance, fixed_fx_stat = compute_fixed_effects(
            effects_files, variances_files, precision_weighted=True
        )

        # Save out fixed effects contrast, variance and z-score
        fixed_effects_filename = Path(
            fixed_effects_dir,
            f"sub-{subj_id}_task-{task_name}_contrast-{contrast_name}_"
            f"rtmodel-rt_centered_stat-fixed-effects.nii.gz"
        )
        fixed_fx_contrast.to_filename(fixed_effects_filename)

        fixed_variance_filename = Path(
            fixed_effects_dir,
            f"sub-{subj_id}_task-{task_name}_contrast-{contrast_name}_"
            f"rtmodel-rt_centered_stat-fixed-effects-variance.nii.gz"
        )
        fixed_fx_variance.to_filename(fixed_variance_filename)

        fixed_stat_filename = Path(
            fixed_effects_dir,
            f"sub-{subj_id}_task-{task_name}_contrast-{contrast_name}_"
            f"rtmodel-rt_centered_stat-fixed-effects-z_score.nii.gz"
        )
        fixed_fx_stat.to_filename(fixed_stat_filename)

        print(f"Fixed effects results for {contrast_name} saved to {fixed_effects_dir}")


    return


if __name__ == "__main__":
    main()
