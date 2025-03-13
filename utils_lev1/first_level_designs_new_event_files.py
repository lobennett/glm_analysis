#TODO: add n/a trial regressors as needed e.g. task switching or nBack tasks
#TODO: get rid of duration_choice stuff
from nilearn.glm.first_level import compute_regressor
import numpy as np
import pandas as pd
import glob

def make_regressor_and_derivative(
    n_scans,
    tr,
    events_df,
    add_deriv,
    amplitude_column=None,
    duration_column=None,
    onset_column=None,
    subset=None,
    demean_amp=False,
    cond_id="cond",
):
    """Creates regressor and derivative using spm + derivative option in
    nilearn's compute_regressor
    Input:
      n_scans: number of timepoints (TRs)
      tr: time resolution in seconds
      events_df: events data frame
      add_deriv: "yes"/"no", whether or not derivatives of regressors should
                 be included
      amplitude_column: Required.  Amplitude column from events_df
      duration_column: Required.  Duration column from events_df
      onset_column: optional.  if not specified "onset" is the default
      subset: optional.  Boolean for subsetting rows of events_df
      demean_amp: Whether amplitude should be mean centered
      cond_id: Name for regressor that is created.  Note "cond_derivative" will
        be assigned as name to the corresponding derivative
    Output:
      regressors: 2 column pandas data frame containing main regressor and derivative convolved
      regressor_3col: 3 column pandas data frame containing onset, duration, and amplitude
    """
    if subset == None:
        events_df["temp_subset"] = True
        subset = "temp_subset == True"
    if onset_column == None:
        onset_column = "onset"
    if amplitude_column == None or duration_column == None:
        print("Must enter amplitude and duration columns")
        return
    if amplitude_column not in events_df.columns:
        print("must specify amplitude column that exists in events_df")
        return
    if duration_column not in events_df.columns:
        print("must specify duration column that exists in events_df")
        return

    reg_3col = events_df.query(subset)[
        [onset_column, duration_column, amplitude_column]
    ]
    reg_3col = reg_3col.rename(
        columns={duration_column: "duration", amplitude_column: "modulation"}
    )

    if demean_amp:
        reg_3col["modulation"] = reg_3col["modulation"] - reg_3col["modulation"].mean()


    if add_deriv == "deriv_yes":
        hrf_model = "spm + derivative"
    else:
        hrf_model = "spm"

    print("HRF model: ", hrf_model)


    regressor_array, regressor_names = compute_regressor(
        np.transpose(np.array(reg_3col)),
        hrf_model,
        # deals with slice timing issue with outputs from fMRIPrep
        np.arange(n_scans) * tr + tr / 2,
        con_id=cond_id,
    )
    regressors = pd.DataFrame(regressor_array, columns=regressor_names)
    return regressors, reg_3col


def define_nuisance_trials(events_df, task):
    if task in ["cuedTS", "nBack", "spatialTS", "flanker", "shapeMatching",
                "spatialTSWCuedTS", "flankerWShapeMatching", "cuedTSWFlanker",
                "spatialTSWShapeMatching", "nBackWShapeMatching", "nBackWSpatialTS",
                "directedForgettingWCuedTS"]:
        omission = ((events_df.key_press == -1) & (events_df.trial_id == "test_trial"))
        commission = (
            (events_df.key_press != events_df.correct_response)
            & (events_df.key_press != -1)
            & (events_df.response_time >= 0.2)
            & (events_df.trial_id == "test_trial")
        )
        rt_too_fast = ((events_df.response_time < 0.2) & (events_df.trial_id == "test_trial"))
        bad_trials = omission | commission | rt_too_fast

    elif task in ["directedForgetting", "directedForgettingWFlanker"]: 
        omission = (events_df.key_press == -1) & (events_df.trial_id == "test_trial")
        commission = (
            (events_df.key_press != events_df.correct_response)
            & (events_df.key_press != -1)
            & (events_df.response_time >= 0.2)
            & (events_df.trial_id == "test_trial")
        )
        rt_too_fast = (events_df.response_time < 0.2) & (events_df.trial_id == "test_trial")
        bad_trials = omission | commission | rt_too_fast

    elif task in ["stopSignal", "goNogo"]:
        omission = (events_df.key_press == -1) & (events_df.trial_type == "go")
        commission = (
            (events_df.key_press != events_df.correct_response)
            & (events_df.key_press != -1)
            & (events_df.trial_type == "go")
            & (events_df.response_time >= 0.2)
        )
        rt_too_fast = (events_df.response_time < 0.2) & (events_df.trial_type == "go")
        bad_trials = omission | commission | rt_too_fast

    elif task in ["stopSignalWDirectedForgetting"]:
        omission = (events_df.key_press == -1) & (
            events_df.trial_type.isin(["go_pos", "go_neg", "go_con"])
        )
        commission = (
            (events_df.key_press != events_df.correct_response)
            & (events_df.key_press != -1)
            & (events_df.trial_type.isin(["go_pos", "go_neg", "go_con"]))
            & (events_df.response_time >= 0.2)
        )
        rt_too_fast = (events_df.response_time < 0.2) & (
            events_df.trial_type.isin(["go_pos", "go_neg", "go_con"])
        )
        bad_trials = omission | commission | rt_too_fast

    elif task in ["stopSignalWFlanker"]:
        omission = (events_df.key_press == -1) & (
            events_df.trial_type.isin(["go_incongruent", "go_congruent"])
        )
        commission = (
            (events_df.key_press != events_df.correct_response)
            & (events_df.key_press != -1)
            & (events_df.trial_type.isin(["go_incongruent", "go_congruent"]))
            & (events_df.response_time >= 0.2)
        )
        rt_too_fast = (events_df.response_time < 0.2) & (
            events_df.trial_type.isin(["go_incongruent", "go_congruent"])
        )
        bad_trials = omission | commission | rt_too_fast
    else:
        raise ValueError(f"Unexpected task type: {task}")

    return 1 * bad_trials, 1 * omission, 1 * commission, 1 * rt_too_fast

def rename_columns(df, prefix):
    onset_column = 'onset' if 'onset' in df.columns else 'button_onset'
    renamed_columns = {}
    for col in df.columns:
        if col == onset_column:
            continue
        else:
            renamed_columns[col] = f"{prefix}_{col}"
    return df.rename(columns=renamed_columns)

def merge_dataframes(df1, df2, prefix1, prefix2):
    onset_col_1 = f"{prefix1}_onset" if f"{prefix1}_onset" in df1.columns else f"{prefix1}_button_onset"
    onset_col_2 = f"{prefix2}_onset" if f"{prefix2}_onset" in df2.columns else f"{prefix2}_button_onset"
    return df1.merge(df2, left_on=onset_col_1, right_on=onset_col_2, how='outer')

def create_simplified_events_df(dfs):
    '''
    '''
    simplified_events_df = pd.DataFrame()
    for df, prefix in dfs:
        df = rename_columns(df, prefix)
        if simplified_events_df.empty:
            simplified_events_df = df
            continue
        else:
            simplified_events_df = simplified_events_df.merge(df, on='onset', how='outer')
    return simplified_events_df

def make_basic_cuedTS_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic cued task switching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "cuedTS")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset="trial_type != 'tn/a_cn/a'",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset="trial_type != 'tn/a_cn/a'",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset="trial_type != 'tn/a_cn/a'",
        demean_amp=False,
        cond_id="rt_fast",
    )
    #add a n/a regressor to tasks that are appropriate
    n_a_regressor, n_a_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'tn/a_cn/a'",
        demean_amp=False,
        cond_id="n/a",
    )

    task_stay_cue_switch, task_stay_cue_switch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tstay_cswitch'",
        demean_amp=False,
        cond_id="task_stay_cue_switch",
    )
    task_stay_cue_stay, task_stay_cue_stay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tstay_cstay'",
        demean_amp=False,
        cond_id="task_stay_cue_stay",
    )
    task_switch_cue_switch, task_switch_cue_switch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tswitch_cswitch'",
        demean_amp=False,
        cond_id="task_switch_cue_switch",
    )

    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (task_stay_cue_switch_3col, 'task_stay_cue_switch'),
        (task_stay_cue_stay_3col, 'task_stay_cue_stay'),
        (task_switch_cue_switch_3col, 'task_switch_cue_switch'),
    ]
    
    design_matrix = pd.concat(
        [
            task_stay_cue_switch,
            task_stay_cue_stay,
            task_switch_cue_switch,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
            n_a_regressor
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "task_switch_cost": "task_switch_cue_switch-task_stay_cue_switch",
        "cue_switch_cost": "task_stay_cue_switch-task_stay_cue_stay",
        "task_switch_cue_switch-task_stay_cue_stay": "task_switch_cue_switch-task_stay_cue_stay",
        "task-baseline": "1/3*(task_stay_cue_switch+task_stay_cue_stay+task_switch_cue_switch)",
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_type != 'tn/a_cn/a' and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_directedForgetting_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic directed forgetting regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "directedForgetting")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="rt_fast",
    )

    memory_and_cue, memory_and_cue_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="duration",
        subset='trial_id == "test_stim" or trial_id == "test_cue"',
        demean_amp=False,
        cond_id="memory_and_cue",
    )

    con, con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "con"',
        demean_amp=False,
        cond_id="con",
    )
    pos, pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "pos"',
        demean_amp=False,
        cond_id="pos",
    )
    neg, neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "neg"',
        demean_amp=False,
        cond_id="neg",
    )
    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (memory_and_cue_3col, 'memory_and_cue'),
        (con_3col, 'con'),
        (pos_3col, 'pos'),
        (neg_3col, 'neg')
    ]

    design_matrix = pd.concat(
        [
            con,
            pos,
            neg,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
            memory_and_cue,
        ],
        axis=1,
    )

    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))

    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "neg-con": "neg-con",
        "task-baseline": "1/4*(con+pos+neg+memory_and_cue)",  # memory_and_cue
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, events_df


def make_basic_flanker_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic flanker regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})

    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "flanker")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="rt_fast",
    )

    congruent, congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type =='congruent'",
        demean_amp=False,
        cond_id="congruent",
    )

    incongruent, incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type =='incongruent'",
        demean_amp=False,
        cond_id="incongruent",
    )
    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (congruent_3col, 'congruent'),
        (incongruent_3col, 'incongruent')
    ]

    design_matrix = pd.concat(
        [
            congruent,
            incongruent,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))

    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "incongruent-congruent": "incongruent-congruent",
        "task-baseline": "1/2*congruent + 1/2*incongruent",  #
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_goNogo_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic go-nogo regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "goNogo")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    go_omission_regressor, go_omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_omission",
    )
    go_commission_regressor, go_commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_commission",
    )
    go_rt_fast, go_rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_rt_fast",
    )
    nogo_failure, nogo_failure_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'nogo_failure'",
        demean_amp=False,
        cond_id="nogo_failure",
    )

    go, go_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go'",
        demean_amp=False,
        cond_id="go",
    )
    nogo_success, nogo_success_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'nogo_success'",
        demean_amp=False,
        cond_id="nogo_success",
    )
    regressor_dfs = [
        (go_omission_3col, 'go_omission'),
        (go_commission_3col, 'go_commission'),
        (go_rt_fast_3col, 'go_rt_fast'),
        (nogo_failure_3col, 'nogo_failure'),
        (go_3col, 'go'),
        (nogo_success_3col, 'nogo_success')
    ]
    design_matrix = pd.concat(
        [
            go,
            nogo_success,
            nogo_failure,
            go_omission_regressor,
            go_commission_regressor,
            go_rt_fast,
            confound_regressors
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "go": "go",  #
        "nogo_success": "nogo_success",  #
        "nogo_success-go": "nogo_success-go",
        "task-baseline": "1/2*go+1/2*nogo_success",  #
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_nBack_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic nback regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "nBack")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    # defined so that omission & commission during n/a trials are not included in nuissance regressors twice
    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="rt_fast",
    )

    mismatch_1back, mismatch_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'mismatch' and delay == 1",
        demean_amp=False,
        cond_id="mismatch_1back",
    )
    match_1back, match_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'match' and delay == 1",
        demean_amp=False,
        cond_id="match_1back",
    )
    mismatch_2back, mismatch_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'mismatch' and delay == 2",
        demean_amp=False,
        cond_id="mismatch_2back",
    )
    match_2back, match_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'match' and delay == 2",
        demean_amp=False,
        cond_id="match_2back",
    )

    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (mismatch_1back_3col, 'mismatch_1back'),
        (match_1back_3col, 'match_1back'),
        (mismatch_2back_3col, 'mismatch_2back'),
        (match_2back_3col, 'match_2back'),
    ]
    design_matrix = pd.concat(
        [
            mismatch_1back,
            match_1back,
            mismatch_2back,
            match_2back,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )

    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)
    
    contrasts = {
        "twoBack-oneBack": "1/2*(mismatch_2back+match_2back-mismatch_1back-match_1back)",
        "match-mismatch": "1/2*(match_2back+match_1back-mismatch_2back-mismatch_1back)",
        "task-baseline": "1/4*(mismatch_1back+match_1back+mismatch_2back+match_2back)",  #
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_type != 'n/a'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_stopSignal_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic stop signal regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "stopSignal")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1
    go_omission_regressor, go_omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_omission",
    )
    go_commission_regressor, go_commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_commission",
    )
    go_rt_fast, go_rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_rt_fast",
    )

    go, go_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go'",
        demean_amp=False,
        cond_id="go",
    )
    stop_success, stop_success_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success'",
        demean_amp=False,
        cond_id="stop_success",
    )
    stop_failure, stop_failure_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure'",
        demean_amp=False,
        cond_id="stop_failure",
    )

    regressor_dfs = [
        (go_omission_3col, 'go_omission'),
        (go_commission_3col, 'go_commission'),
        (go_rt_fast_3col, 'go_rt_fast'),
        (go_3col, 'go'),
        (stop_success_3col, 'stop_success'),
        (stop_failure_3col, 'stop_failure')
    ]
    design_matrix = pd.concat(
        [
            go,
            stop_success,
            stop_failure,
            go_omission_regressor,
            go_commission_regressor,
            go_rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "go": "go",  #
        "stop_success": "stop_success",  #
        "stop_failure": "stop_failure",  #
        "stop_success-go": "stop_success-go",
        "stop_failure-go": "stop_failure-go",
        "stop_success-stop_failure": "stop_success-stop_failure",
        "stop_failure-stop_success": "stop_failure-stop_success",
        "task-baseline": "1/3*go + 1/3*stop_failure + 1/3*stop_success",  #
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_shapeMatching_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic shape matching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "shapeMatching")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1
    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="rt_fast",
    )

    SSS, SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'SSS'",
        demean_amp=False,
        cond_id="SSS",
    )
    SDD, SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'SDD'",
        demean_amp=False,
        cond_id="SDD",
    )
    SNN, SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'SNN'",
        demean_amp=False,
        cond_id="SNN",
    )
    DSD, DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'DSD'",
        demean_amp=False,
        cond_id="DSD",
    )
    DNN, DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'DNN'",
        demean_amp=False,
        cond_id="DNN",
    )
    DDD, DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'DDD'",
        demean_amp=False,
        cond_id="DDD",
    )
    DDS, DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'DDS'",
        demean_amp=False,
        cond_id="DDS",
    )
    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (SSS_3col, 'SSS'),
        (SDD_3col, 'SDD'),
        (SNN_3col, 'SNN'),
        (DSD_3col, 'DSD'),
        (DDD_3col, 'DDD'),
        (DDS_3col, 'DDS'),
        (DNN_3col, 'DNN')
    ]
    design_matrix = pd.concat(
        [
            SSS,
            SDD,
            SNN,
            DSD,
            DDD,
            DDS,
            DNN,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )

    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))

    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "task-baseline": "1/7*(SSS+SDD+SNN+DSD+DDD+DDS+DNN)",
        "main_vars": "1/3*(SDD+DDD+DDS)-1/2*(SNN+DNN)",
        "SSS": "SSS",
        "SDD": "SDD",
        "SNN": "SNN",
        "DSD": "DSD",
        "DDD": "DDD",
        "DDS": "DDS",
        "DNN": "DNN",
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_spatialTS_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic spatial task switching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "spatialTS")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1
    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="rt_fast",
    )

    task_stay_cue_switch, task_stay_cue_switch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tstay_cswitch'",
        demean_amp=False,
        cond_id="task_stay_cue_switch",
    )
    task_stay_cue_stay, task_stay_cue_stay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tstay_cstay'",
        demean_amp=False,
        cond_id="task_stay_cue_stay",
    )
    task_switch_cue_switch, task_switch_cue_switch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'tswitch_cswitch'",
        demean_amp=False,
        cond_id="task_switch_cue_switch",
    )
    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (task_stay_cue_switch_3col, 'task_stay_cue_switch'),
        (task_stay_cue_stay_3col, 'task_stay_cue_stay'),
        (task_switch_cue_switch_3col, 'task_switch_cue_switch')
    ]
    design_matrix = pd.concat(
        [
            task_stay_cue_switch,
            task_stay_cue_stay,
            task_switch_cue_switch,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "task_switch_cost": "task_switch_cue_switch-task_stay_cue_switch",
        "cue_switch_cost": "task_stay_cue_switch-task_stay_cue_stay",
        "task_switch_cue_switch-task_stay_cue_stay": "task_switch_cue_switch-task_stay_cue_stay",
        "task-baseline": "1/3*(task_stay_cue_switch+task_stay_cue_stay+task_switch_cue_switch)",
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_type != 'n/a'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_directedForgettingWFlanker_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic directed forgetting + flanker regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "directedForgettingWFlanker")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="rt_fast",
    )
    memory_and_cue, memory_and_cue_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="duration",
        subset='trial_id == "test_cue" or trial_id == "test_four_letters"',
        demean_amp=False,
        cond_id="memory_and_cue",
    )

    incongruent_con, incongruent_con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "incongruent_con"',
        demean_amp=False,
        cond_id="incongruent_con",
    )
    incongruent_pos, incongruent_pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "incongruent_pos"',
        demean_amp=False,
        cond_id="incongruent_pos",
    )
    incongruent_neg, incongruent_neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "incongruent_neg"',
        demean_amp=False,
        cond_id="incongruent_neg",
    )
    congruent_con, congruent_con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "congruent_con"',
        demean_amp=False,
        cond_id="congruent_con",
    )
    congruent_pos, congruent_pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "congruent_pos"',
        demean_amp=False,
        cond_id="congruent_pos",
    )
    congruent_neg, congruent_neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='key_press == correct_response and response_time >= 0.2 and trial_type == "congruent_neg"',
        demean_amp=False,
        cond_id="congruent_neg",
    )
    regressor_dfs = [
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
        (incongruent_con_3col, 'incongruent_con'),
        (incongruent_pos_3col, 'incongruent_pos'),
        (incongruent_neg_3col, 'incongruent_neg'),
        (congruent_con_3col, 'congruent_con'),
        (congruent_pos_3col, 'congruent_pos'),
        (congruent_neg_3col, 'congruent_neg'),
    ]
    design_matrix = pd.concat(
        [
            incongruent_con,
            incongruent_pos,
            incongruent_neg,
            congruent_con,
            congruent_pos,
            congruent_neg,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
            memory_and_cue,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "congruent_neg-congruent_con": "congruent_neg-congruent_con",
        "incongruent_con-congruent_con": "incongruent_con-congruent_con",
        "(incongruent_neg-incongruent_con)-(congruent_neg-congruent_con)": "1/2*(incongruent_neg+congruent_con)-1/2*(incongruent_con+congruent_neg)",
        "congruent_pos": "congruent_pos",
        "congruent_neg": "congruent_neg",
        "congruent_con": "congruent_con",
        "incongruent_pos": "incongruent_pos",
        "incongruent_neg": "incongruent_neg",
        "incongruent_con": "incongruent_con",
        "task-baseline": "1/7*(congruent_pos+congruent_neg+congruent_con+incongruent_pos+incongruent_neg+incongruent_con+memory_and_cue)",  # memory_and_cue
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_stopSignalWDirectedForgetting_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,  # there was a comma missing here
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic stop signal + DF regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "stopSignalWDirectedForgetting")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    go_omission_regressor, go_omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_omission",
    )
    go_commission_regressor, go_commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_commission",
    )
    go_rt_fast, go_rt_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="go_rt_fast",
    )
    memory_and_cue = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="duration",
        subset='trial_id == "test_stim" or trial_id == "test_cue"',
        demean_amp=False,
        cond_id="memory_and_cue",
    )

    go_pos, go_pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go_pos'",
        demean_amp=False,
        cond_id="go_pos",
    )
    go_neg, go_neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go_neg'",
        demean_amp=False,
        cond_id="go_neg",
    )
    go_con, go_con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go_con'",
        demean_amp=False,
        cond_id="go_con",
    )
    stop_success_pos, stop_success_pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success_pos'",
        demean_amp=False,
        cond_id="stop_success_pos",
    )
    stop_success_neg, stop_success_neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success_neg'",
        demean_amp=False,
        cond_id="stop_success_neg",
    )
    stop_success_con, stop_success_con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success_con'",
        demean_amp=False,
        cond_id="stop_success_con",
    )
    stop_failure_pos, stop_failure_pos_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure_pos'",
        demean_amp=False,
        cond_id="stop_failure_pos",
    )
    stop_failure_neg, stop_failure_neg_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure_neg'",
        demean_amp=False,
        cond_id="stop_failure_neg",
    )
    stop_failure_con, stop_failure_con_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure_con'",
        demean_amp=False,
        cond_id="stop_failure_con",
    )
    regressor_dfs = [
        (go_pos_3col, 'go_pos'),
        (go_neg_3col, 'go_neg'),
        (go_con_3col, 'go_con'),
        (stop_success_pos_3col, 'stop_success_pos'),
        (stop_success_neg_3col, 'stop_success_neg'),
        (stop_success_con_3col, 'stop_success_con'),
        (stop_failure_pos_3col, 'stop_failure_pos'),
        (stop_failure_neg_3col, 'stop_failure_neg'),
        (stop_failure_con_3col, 'stop_failure_con'),
        (go_omission_3col, 'go_omission'),
        (go_commission_3col, 'go_commission'),
        (go_rt_3col, 'go_rt_fast'),
        (memory_and_cue_3col, 'memory_and_cue')
    ]
    design_matrix = pd.concat(
        [
            go_pos,
            go_neg,
            go_con,
            stop_success_pos,
            stop_success_neg,
            stop_success_con,
            stop_failure_pos,
            stop_failure_neg,
            stop_failure_con,
            go_omission_regressor,
            go_commission_regressor,
            go_rt_fast,
            confound_regressors,
            memory_and_cue,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "(stop_success_con+stop_success_pos+stop_success_neg)-(go_con+go_pos_+go_neg)": "1/3*(stop_success_con+stop_success_pos+stop_success_neg)-1/3*(go_con+go_pos+go_neg)",
        "(stop_failure_con+stop_failure_pos+stop_failure_neg)-(go_con+go_pos_+go_neg)": "1/3*(stop_failure_con+stop_failure_pos+stop_failure_neg)-1/3*(go_con+go_pos+go_neg)",
        "(stop_success_neg-go_neg)-(stop_success_con-go_con)": "1/2*(stop_success_neg-go_neg)-1/2*(stop_success_con-go_con)",
        "(stop_failure_neg-go_neg)-(stop_failure_con-go_con)": "1/2*(stop_failure_neg-go_neg)-1/2*(stop_failure_con-go_con)",
        "go_neg-go_con": "go_neg-go_con",
        "stop_success_con-go_con": "stop_success_con-go_con",
        "go_pos": "go_pos",
        "go_neg": "go_neg",
        "go_con": "go_con",
        "stop_success_pos": "stop_success_pos",
        "stop_success_neg": "stop_success_neg",
        "stop_success_con": "stop_success_con",
        "stop_failure_pos": "stop_failure_pos",
        "stop_failure_neg": "stop_failure_neg",
        "stop_failure_con": "stop_failure_con",
        "task-baseline": "1/10*(go_pos+go_neg+go_con+stop_success_pos+stop_success_neg+stop_success_con+stop_failure_pos+stop_failure_neg+stop_failure_con+memory_and_cue)",  # memory_and_cue
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="key_press == correct_response and response_time >= 0.2 and trial_id == 'test_trial'",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df


def make_basic_stopSignalWFlanker_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic stop + flanker regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "stopSignalWFlanker")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1
    go_omission_regressor, go_omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_omission",
    )
    go_commission_regressor, go_commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_commission",
    )
    go_rt_fast, go_rt_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset=None,
        demean_amp=False,
        cond_id="go_rt_fast",
    )

    go_congruent, go_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go_congruent'",
        demean_amp=False,
        cond_id="go_congruent",
    )
    go_incongruent, go_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="key_press == correct_response and response_time >= 0.2 and trial_type == 'go_incongruent'",
        demean_amp=False,
        cond_id="go_incongruent",
    )
    stop_success_congruent, stop_success_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success_congruent'",
        demean_amp=False,
        cond_id="stop_success_congruent",
    )
    stop_success_incongruent, stop_success_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_success_incongruent'",
        demean_amp=False,
        cond_id="stop_success_incongruent",
    )
    stop_failure_congruent, stop_failure_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure_congruent'",
        demean_amp=False,
        cond_id="stop_failure_congruent",
    )
    stop_failure_incongruent, stop_failure_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset="trial_type == 'stop_failure_incongruent'",
        demean_amp=False,
        cond_id="stop_failure_incongruent",
    )
    regressor_dfs = [
        (go_congruent_3col, 'go_congruent'),
        (go_incongruent_3col, 'go_incongruent'),
        (stop_success_congruent_3col, 'stop_success_congruent'),
        (stop_success_incongruent_3col, 'stop_success_incongruent'),
        (stop_failure_congruent_3col, 'stop_failure_congruent'),
        (stop_failure_incongruent_3col, 'stop_failure_incongruent'),
        (go_omission_3col, 'go_omission'),
        (go_commission_3col, 'go_commission'),
        (go_rt_3col, 'go_rt_fast')
    ]
    design_matrix = pd.concat(
        [
            go_incongruent,
            go_congruent,
            stop_success_incongruent,
            stop_success_congruent,
            stop_failure_incongruent,
            stop_failure_congruent,
            go_omission_regressor,
            go_commission_regressor,
            go_rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))

    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        "(stop_success_congruent+stop_success_incongruent)-(go_congruent+go_incongruent)": "1/2*(stop_success_congruent+stop_success_incongruent)-1/2*(go_congruent+go_incongruent)",
        "(stop_failure_congruent+stop_failure_incongruent)-(go_congruent+go_incongruent)": "1/2*(stop_failure_congruent+stop_failure_incongruent)-1/2*(go_congruent+go_incongruent)",
        "(stop_success_incongruent-go_incongruent)-(stop_success_congruent-go_congruent)": "1/2*(stop_success_incongruent-go_incongruent)-1/2*(stop_success_congruent-go_congruent)",
        "(stop_failure_incongruent-go_incongruent)-(stop_failure_congruent-go_congruent)": "1/2*(stop_failure_incongruent-go_incongruent)-1/2*(stop_failure_congruent-go_congruent)",
        "stop_success_congruent-go_congruent": "stop_success_congruent-go_congruent",
        "go_incongruent-go_congruent": "go_incongruent-go_congruent",
        "go_congruent": "go_congruent",
        "go_incongruent": "go_incongruent",
        "stop_success_congruent": "stop_success_congruent",
        "stop_success_incongruent": "stop_success_incongruent",
        "stop_failure_congruent": "stop_failure_incongruent",
        "stop_failure_incongruent": "stop_failure_incongruent",
        "task-baseline": "1/6*(go_congruent+go_incongruent+stop_success_congruent+stop_success_incongruent+stop_failure_congruent+stop_failure_incongruent)",
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset=rt_subset,
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"

    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_spatialTSWCuedTS_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic spatialTS + cuedTS regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "spatialTSWCuedTS")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset="trial_type != 'n/a'",
        demean_amp=False,
        cond_id="rt_fast",
    )

    cuedtstaycstay_spatialtstaycstay, cuedtstaycstay_spatialtstaycstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycstay_spatialtstaycstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycstay_spatialtstaycstay",
    )
    cuedtstaycstay_spatialtstaycswitch, cuedtstaycstay_spatialtstaycswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycstay_spatialtstaycswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycstay_spatialtstaycswitch",
    )
    cuedtstaycstay_spatialtswitchcswitch, cuedtstaycstay_spatialtswitchcswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycstay_spatialtswitchcswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycstay_spatialtswitchcswitch",
    )
    cuedtstaycswitch_spatialtstaycstay, cuedtstaycswitch_spatialtstaycstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycswitch_spatialtstaycstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycswitch_spatialtstaycstay",
    )
    cuedtstaycswitch_spatialtstaycswitch, cuedtstaycswitch_spatialtstaycswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycswitch_spatialtstaycswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycswitch_spatialtstaycswitch",
    )
    cuedtstaycswitch_spatialtswitchcswitch, cuedtstaycswitch_spatialtswitchcswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtstaycswitch_spatialtswitchcswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtstaycswitch_spatialtswitchcswitch",
    )
    cuedtswitchcswitch_spatialtstaycstay, cuedtswitchcswitch_spatialtstaycstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtswitchcswitch_spatialtstaycstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtswitchcswitch_spatialtstaycstay",
    )
    cuedtswitchcswitch_spatialtstaycswitch, cuedtswitchcswitch_spatialtstaycswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtswitchcswitch_spatialtstaycswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtswitchcswitch_spatialtstaycswitch",
    )
    cuedtswitchcswitch_spatialtswitchcswitch, cuedtswitchcswitch_spatialtswitchcswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cuedtswitchcswitch_spatialtswitchcswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cuedtswitchcswitch_spatialtswitchcswitch",
    )

    regressor_dfs = [
        (cuedtstaycstay_spatialtstaycstay_3col, 'cuedtstaycstay_spatialtstaycstay'),
        (cuedtstaycstay_spatialtstaycswitch_3col, 'cuedtstaycstay_spatialtstaycswitch'),
        (cuedtstaycstay_spatialtswitchcswitch_3col, 'cuedtstaycstay_spatialtswitchcswitch'),
        (cuedtstaycswitch_spatialtstaycstay_3col, 'cuedtstaycswitch_spatialtstaycstay'),
        (cuedtstaycswitch_spatialtstaycswitch_3col, 'cuedtstaycswitch_spatialtstaycswitch'),
        (cuedtstaycswitch_spatialtswitchcswitch_3col, 'cuedtstaycswitch_spatialtswitchcswitch'),
        (cuedtswitchcswitch_spatialtstaycstay_3col, 'cuedtswitchcswitch_spatialtstaycstay'),
        (cuedtswitchcswitch_spatialtstaycswitch_3col, 'cuedtswitchcswitch_spatialtstaycswitch'),
        (cuedtswitchcswitch_spatialtswitchcswitch_3col, 'cuedtswitchcswitch_spatialtswitchcswitch'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            cuedtstaycstay_spatialtstaycstay,
            cuedtstaycstay_spatialtstaycswitch,
            cuedtstaycstay_spatialtswitchcswitch,
            cuedtstaycswitch_spatialtstaycstay,
            cuedtstaycswitch_spatialtstaycswitch,
            cuedtstaycswitch_spatialtswitchcswitch,
            cuedtswitchcswitch_spatialtstaycstay,
            cuedtswitchcswitch_spatialtstaycswitch,
            cuedtswitchcswitch_spatialtswitchcswitch,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "cuedtstaycstay_spatialtstaycstay": "cuedtstaycstay_spatialtstaycstay",
        "cuedtstaycstay_spatialtstaycswitch": "cuedtstaycstay_spatialtstaycswitch",
        "cuedtstaycstay_spatialtswitchcswitch": "cuedtstaycstay_spatialtswitchcswitch",
        "cuedtstaycswitch_spatialtstaycstay": "cuedtstaycswitch_spatialtstaycstay",
        "cuedtstaycswitch_spatialtstaycswitch": "cuedtstaycswitch_spatialtstaycswitch",
        "cuedtstaycswitch_spatialtswitchcswitch": "cuedtstaycswitch_spatialtswitchcswitch",
        "cuedtswitchcswitch_spatialtstaycstay": "cuedtswitchcswitch_spatialtstaycstay",
        "cuedtswitchcswitch_spatialtstaycswitch": "cuedtswitchcswitch_spatialtstaycswitch",
        "cuedtswitchcswitch_spatialtswitchcswitch": "cuedtswitchcswitch_spatialtswitchcswitch",
        #cue switch cost for cuedTS 
        "cuedtstaycswitch_spatialtstaycstay-cuedtstaycstay_spatialtstaycstay": "cuedtstaycswitch_spatialtstaycstay-cuedtstaycstay_spatialtstaycstay",
        #task switch cost for cuedTS
        "cuedtswitchcswitch_spatialtstaycstay-cuedtstaycswitch_spatialtstaycstay": "cuedtswitchcswitch_spatialtstaycstay-cuedtstaycswitch_spatialtstaycstay",
        #cue switch cost for spatialTS
        "cuedtstaycstay_spatialtstaycswitch-cuedtstaycstay_spatialtstaycstay": "cuedtstaycstay_spatialtstaycswitch-cuedtstaycstay_spatialtstaycstay",
        #task switch cost for spatialTS
        "cuedtstaycstay_spatialtswitchcswitch-cuedtstaycstay_spatialtstaycswitch": "cuedtstaycstay_spatialtswitchcswitch-cuedtstaycstay_spatialtstaycswitch",
        #cue switch cost for cuedTS averaged across other trials
        "(cuedtstaycswitch_spatialtstaycstay+cuedtstaycswitch_spatialtstaycswitch+cuedtstaycswitch_spatialtswitchcswitch)-(cuedtstaycstay_spatialtstaycstay+cuedtstaycstay_spatialtstaycswitch+cuedtstaycstay_spatialtswitchcswitch)": 
        "1/3*(cuedtstaycswitch_spatialtstaycstay+cuedtstaycswitch_spatialtstaycswitch+cuedtstaycswitch_spatialtswitchcswitch)-1/3*(cuedtstaycstay_spatialtstaycstay+cuedtstaycstay_spatialtstaycswitch+cuedtstaycstay_spatialtswitchcswitch)",
        #task switch cost for cuedTS averaged across other trials
        "(cuedtswitchcswitch_spatialtstaycstay+cuedtswitchcswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtswitchcswitch)-(cuedtstaycswitch_spatialtstaycstay+cuedtstaycswitch_spatialtstaycswitch+cuedtstaycswitch_spatialtswitchcswitch)":
        "1/3*(cuedtswitchcswitch_spatialtstaycstay+cuedtswitchcswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtswitchcswitch)-1/3*(cuedtstaycswitch_spatialtstaycstay+cuedtstaycswitch_spatialtstaycswitch+cuedtstaycswitch_spatialtswitchcswitch)",
        #cue switch cost for spatialTS averaged across other trials
        "(cuedtstaycstay_spatialtstaycswitch+cuedtstaycswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtstaycswitch)-(cuedtstaycstay_spatialtstaycstay+cuedtstaycswitch_spatialtstaycstay+cuedtswitchcswitch_spatialtstaycstay)":
        "1/3*(cuedtstaycstay_spatialtstaycswitch+cuedtstaycswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtstaycswitch)-1/3*(cuedtstaycstay_spatialtstaycstay+cuedtstaycswitch_spatialtstaycstay+cuedtswitchcswitch_spatialtstaycstay)",
        #task switch cost for spatialTS averaged across other trials
        "(cuedtstaycstay_spatialtswitchcswitch+cuedtstaycswitch_spatialtswitchcswitch+cuedtswitchcswitch_spatialtswitchcswitch)-(cuedtstaycstay_spatialtstaycswitch+cuedtstaycswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtstaycswitch)":
        "1/3*(cuedtstaycstay_spatialtswitchcswitch+cuedtstaycswitch_spatialtswitchcswitch+cuedtswitchcswitch_spatialtswitchcswitch)-1/3*(cuedtstaycstay_spatialtstaycswitch+cuedtstaycswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtstaycswitch)",
        #interaction for cue switch cost
        "(cuedtstaycswitch_spatialtstaycswitch-cuedtstaycstay_spatialtstaycswitch)-(cuedtstaycswitch_spatialtstaycstay-cuedtstaycstay_spatialtstaycstay)":
        "1/2*(cuedtstaycswitch_spatialtstaycswitch-cuedtstaycstay_spatialtstaycswitch)-1/2*(cuedtstaycswitch_spatialtstaycstay-cuedtstaycstay_spatialtstaycstay)",
        #interaction for task switch cost
        "(cuedtswitchcswitch_spatialtswitchcswitch-cuedtstaycswitch_spatialtswitchcswitch)-(cuedtswitchcswitch_spatialtstaycswitch-cuedtstaycswitch_spatialtstaycswitch)":
        "1/2*(cuedtswitchcswitch_spatialtswitchcswitch-cuedtstaycswitch_spatialtswitchcswitch)-1/2*(cuedtswitchcswitch_spatialtstaycswitch-cuedtstaycswitch_spatialtstaycswitch)",
        #task - baseline
        "task-baseline": "1/9*(cuedtstaycstay_spatialtstaycstay+cuedtstaycstay_spatialtstaycswitch+cuedtstaycstay_spatialtswitchcswitch+cuedtstaycswitch_spatialtstaycstay+cuedtstaycswitch_spatialtstaycswitch+cuedtstaycswitch_spatialtswitchcswitch+cuedtswitchcswitch_spatialtstaycstay+cuedtswitchcswitch_spatialtstaycswitch+cuedtswitchcswitch_spatialtswitchcswitch)",
    }

    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_flankerWShapeMatching_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break 
):
    """Creates basic flanker + shapeMatching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "flankerWShapeMatching")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        demean_amp=False,
        cond_id="rt_fast",
    )

    congruent_SSS, congruent_SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_SSS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_SSS",
    )
    congruent_SDD, congruent_SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_SDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_SDD",
    )
    congruent_SNN, congruent_SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_SNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_SNN",
    )
    congruent_DSD, congruent_DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_DSD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_DSD",
    )
    congruent_DNN, congruent_DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_DNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_DNN",
    )
    congruent_DDD, congruent_DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_DDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_DDD",
    )
    congruent_DDS, congruent_DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "congruent_DDS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="congruent_DDS",
    )
    incongruent_SSS, incongruent_SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_SSS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_SSS",
    )
    incongruent_SDD, incongruent_SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_SDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_SDD",
    )
    incongruent_SNN, incongruent_SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_SNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_SNN",
    )
    incongruent_DSD, incongruent_DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_DSD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_DSD",
    )
    incongruent_DNN, incongruent_DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_DNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_DNN",
    )
    incongruent_DDD, incongruent_DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_DDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_DDD",
    )
    incongruent_DDS, incongruent_DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "incongruent_DDS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="incongruent_DDS",
    )
    regressor_dfs = [
        (congruent_SSS_3col, 'congruent_SSS'),
        (congruent_SDD_3col, 'congruent_SDD'),
        (congruent_SNN_3col, 'congruent_SNN'),
        (congruent_DSD_3col, 'congruent_DSD'),
        (congruent_DNN_3col, 'congruent_DNN'),
        (congruent_DDD_3col, 'congruent_DDD'),
        (congruent_DDS_3col, 'congruent_DDS'),
        (incongruent_SSS_3col, 'incongruent_SSS'),
        (incongruent_SDD_3col, 'incongruent_SDD'),
        (incongruent_SNN_3col, 'incongruent_SNN'),
        (incongruent_DSD_3col, 'incongruent_DSD'),
        (incongruent_DNN_3col, 'incongruent_DNN'),
        (incongruent_DDD_3col, 'incongruent_DDD'),
        (incongruent_DDS_3col, 'incongruent_DDS'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            congruent_SSS,
            congruent_SDD,
            congruent_SNN,
            congruent_DSD,
            congruent_DNN,
            congruent_DDD,
            congruent_DDS,
            incongruent_SSS,
            incongruent_SDD,
            incongruent_SNN,
            incongruent_DSD,
            incongruent_DNN,
            incongruent_DDD,
            incongruent_DDS,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "congruent_SSS": "congruent_SSS",
        "congruent_SDD": "congruent_SDD",
        "congruent_SNN": "congruent_SNN",
        "congruent_DSD": "congruent_DSD",
        "congruent_DNN": "congruent_DNN",
        "congruent_DDD": "congruent_DDD",
        "congruent_DDS": "congruent_DDS",
        "incongruent_SSS": "incongruent_SSS",
        "incongruent_SDD": "incongruent_SDD",
        "incongruent_SNN": "incongruent_SNN",
        "incongruent_DSD": "incongruent_DSD",
        "incongruent_DNN": "incongruent_DNN",
        "incongruent_DDD": "incongruent_DDD",
        "incongruent_DDS": "incongruent_DDS",
        #incongruent-congruent while shapeMatching is "off"
        "(incongruent_SNN+incongruent_DNN)-(congruent_SNN+congruent_DNN)": "1/2*(incongruent_SNN+incongruent_DNN)-1/2*(congruent_SNN+congruent_DNN)",
        #main vars while flanker is "off"
        "(congruent_SDD+congruent_DDD+congruent_DDS)-(congruent_SNN+congruent_DNN)": "1/3*(congruent_SDD+congruent_DDD+congruent_DDS)-1/2*(congruent_SNN+congruent_DNN)",
        #incongruent-congruent across all other trial types in shapeMatching
        "(incongruent_SSS+incongruent_SDD+incongruent_SNN+incongruent_DSD+incongruent_DNN+incongruent_DDD+incongruent_DDS)-(congruent_SSS+congruent_SDD+congruent_SNN+congruent_DSD+congruent_DNN+congruent_DDD+congruent_DDS)":
        "1/7*(incongruent_SSS+incongruent_SDD+incongruent_SNN+incongruent_DSD+incongruent_DNN+incongruent_DDD+incongruent_DDS)-1/7*(congruent_SSS+congruent_SDD+congruent_SNN+congruent_DSD+congruent_DNN+congruent_DDD+congruent_DDS)",
        #main vars across all other flanker trial types
        "(congruent_SDD+congruent_DDD+congruent_DDS+incongruent_SDD+incongruent_DDD+incongruent_DDS)-(congruent_SNN+congruent_DNN+incongruent_SNN+incongruent_DNN)":
        "1/6*(congruent_SDD+congruent_DDD+congruent_DDS+incongruent_SDD+incongruent_DDD+incongruent_DDS)-1/4*(congruent_SNN+congruent_DNN+incongruent_SNN+incongruent_DNN)",
        #interaction for each trial type
        "((incongruent_SDD+incongruent_DDD+incongruent_DDS)-(congruent_SDD+congruent_DDD+congruent_DDS))-((incongruent_SNN+incongruent_DNN)-(congruent_SNN+congruent_DNN))":
        "(1/3*(incongruent_SDD+incongruent_DDD+incongruent_DDS)-1/3*(congruent_SDD+congruent_DDD+congruent_DDS))-(1/2*(incongruent_SNN+incongruent_DNN)-1/2*(congruent_SNN+congruent_DNN))",
        #task - baseline
        "task-baseline": "1/14*(congruent_SSS+congruent_SDD+congruent_SNN+congruent_DSD+congruent_DNN+congruent_DDD+congruent_DDS+incongruent_SSS+incongruent_SDD+incongruent_SNN+incongruent_DSD+incongruent_DNN+incongruent_DDD+incongruent_DDS)",
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_cuedTSWFlanker_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break 
):
    """Creates basic cuedTS + flanker regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "cuedTSWFlanker")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset = '"cn/a_tn/a" not in trial_type',
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset = '"cn/a_tn/a" not in trial_type',
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset = '"cn/a_tn/a" not in trial_type',
        demean_amp=False,
        cond_id="rt_fast",
    )

    cstay_tstay_congruent, cstay_tstay_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cstay_tstay_congruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cstay_tstay_congruent",
    )
    cstay_tstay_incongruent, cstay_tstay_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cstay_tstay_incongruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cstay_tstay_incongruent",
    )
    cswitch_tswitch_congruent, cswitch_tswitch_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cswitch_tswitch_congruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cswitch_tswitch_congruent",
    )
    cswitch_tswitch_incongruent, cswitch_tswitch_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cswitch_tswitch_incongruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cswitch_tswitch_incongruent",
    )
    cswitch_tstay_congruent, cswitch_tstay_congruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cswitch_tstay_congruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cswitch_tstay_congruent",
    )
    cswitch_tstay_incongruent, cswitch_tstay_incongruent_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "cswitch_tstay_incongruent" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="cswitch_tstay_incongruent",
    )
    
    regressor_dfs = [
        (cstay_tstay_congruent_3col, 'cstay_tstay_congruent'),
        (cstay_tstay_incongruent_3col, 'cstay_tstay_incongruent'),
        (cswitch_tswitch_congruent_3col, 'cswitch_tswitch_congruent'),
        (cswitch_tswitch_incongruent_3col, 'cswitch_tswitch_incongruent'),
        (cswitch_tstay_congruent_3col, 'cswitch_tstay_congruent'),
        (cswitch_tstay_incongruent_3col, 'cswitch_tstay_incongruent'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
    [
        cstay_tstay_congruent,
        cstay_tstay_incongruent,
        cswitch_tswitch_congruent,
        cswitch_tswitch_incongruent,
        cswitch_tstay_congruent,
        cswitch_tstay_incongruent,
        omission_regressor,
        commission_regressor,
        rt_fast,
        confound_regressors,
    ],
    axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))

    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "cstay_tstay_congruent": "cstay_tstay_congruent",
        "cstay_tstay_incongruent": "cstay_tstay_incongruent",
        "cswitch_tswitch_congruent": "cswitch_tswitch_congruent",
        "cswitch_tswitch_incongruent": "cswitch_tswitch_incongruent",
        "cswitch_tstay_congruent": "cswitch_tstay_congruent",
        "cswitch_tstay_incongruent": "cswitch_tstay_incongruent",
        #incongruent-congruent while cuedTS is "off"
        "cstay_tstay_incongruent-cstay_tstay_congruent": "cstay_tstay_incongruent-cstay_tstay_congruent",
        #cue switch cost while flanker is "off"
        "cswitch_tstay_congruent-cstay_tstay_congruent": "cswitch_tstay_congruent-cstay_tstay_congruent",
        #task switch cost while flanker is "off"
        "cswitch_tswitch_congruent-cswitch_tstay_congruent": "cswitch_tswitch_congruent-cswitch_tstay_congruent",
        #incongruent-congruent across all cuedTS trial types
        "(cstay_tstay_incongruent+cswitch_tswitch_incongruent+cswitch_tstay_incongruent)-(cstay_tstay_congruent+cswitch_tswitch_congruent+cswitch_tstay_congruent)":
        "1/3*(cstay_tstay_incongruent+cswitch_tswitch_incongruent+cswitch_tstay_incongruent)-1/3*(cstay_tstay_congruent+cswitch_tswitch_congruent+cswitch_tstay_congruent)",
        #cue switch cost across all flanker trial types
        "(cswitch_tstay_congruent+cswitch_tstay_incongruent)-(cstay_tstay_congruent+cstay_tstay_incongruent)":
        "1/2*(cswitch_tstay_congruent+cswitch_tstay_incongruent)-1/2*(cstay_tstay_congruent+cstay_tstay_incongruent)",
        #task switch cost across all flanker trial types
        "(cswitch_tswitch_congruent+cswitch_tswitch_incongruent)-(cswitch_tstay_congruent+cswitch_tstay_incongruent)":
        "1/2*(cswitch_tswitch_congruent+cswitch_tswitch_incongruent)-1/2*(cswitch_tstay_congruent+cswitch_tstay_incongruent)",
        #interaction for cue switch cost
        "(cswitch_tstay_incongruent-cstay_tstay_incongruent)-(cswitch_tstay_congruent-cstay_tstay_congruent)":
        "1/2*(cswitch_tstay_incongruent-cstay_tstay_incongruent)-1/2*(cswitch_tstay_congruent-cstay_tstay_congruent)",
        #interaction for task switch cost
        "(cswitch_tswitch_incongruent-cswitch_tstay_incongruent)-(cswitch_tswitch_congruent-cswitch_tstay_congruent)":
        "1/2*(cswitch_tswitch_incongruent-cswitch_tstay_incongruent)-1/2*(cswitch_tswitch_congruent-cswitch_tstay_congruent)",
        #task - baseline
        "task-baseline": "1/6*(cstay_tstay_congruent+cstay_tstay_incongruent+cswitch_tswitch_congruent+cswitch_tswitch_incongruent+cswitch_tstay_congruent+cswitch_tstay_incongruent)",
    }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_spatialTSWShapeMatching_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break 
):
    """Creates basic spatialTS + shapeMatching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "spatialTSWShapeMatching")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="rt_fast",
    )

    tstay_cstay_SSS, tstay_cstay_SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_SSS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_SSS",
    )
    tstay_cstay_SDD, tstay_cstay_SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_SDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_SDD",
    )
    tstay_cstay_SNN, tstay_cstay_SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_SNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_SNN",
    )
    tstay_cstay_DSD, tstay_cstay_DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_DSD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_DSD",
    )
    tstay_cstay_DNN, tstay_cstay_DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_DNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_DNN",
    )
    tstay_cstay_DDD, tstay_cstay_DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_DDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_DDD",
    )
    tstay_cstay_DDS, tstay_cstay_DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cstay_DDS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cstay_DDS",
    )
    tstay_cswitch_SSS, tstay_cswitch_SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_SSS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_SSS",
    )
    tstay_cswitch_SDD, tstay_cswitch_SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_SDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_SDD",
    )
    tstay_cswitch_SNN, tstay_cswitch_SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_SNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_SNN",
    )
    tstay_cswitch_DSD, tstay_cswitch_DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_DSD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_DSD",
    )
    tstay_cswitch_DNN, tstay_cswitch_DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_DNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_DNN",
    )
    tstay_cswitch_DDD, tstay_cswitch_DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_DDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_DDD",
    )
    tstay_cswitch_DDS, tstay_cswitch_DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tstay_cswitch_DDS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tstay_cswitch_DDS",
    )
    tswitch_cswitch_SSS, tswitch_cswitch_SSS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_SSS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_SSS",
    )
    tswitch_cswitch_SDD, tswitch_cswitch_SDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_SDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_SDD",
    )
    tswitch_cswitch_SNN, tswitch_cswitch_SNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_SNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_SNN",
    )
    tswitch_cswitch_DSD, tswitch_cswitch_DSD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_DSD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_DSD",
    )
    tswitch_cswitch_DNN, tswitch_cswitch_DNN_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_DNN" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_DNN",
    )
    tswitch_cswitch_DDD, tswitch_cswitch_DDD_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_DDD" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_DDD",
    )
    tswitch_cswitch_DDS, tswitch_cswitch_DDS_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "tswitch_cswitch_DDS" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="tswitch_cswitch_DDS",
    )
    
    regressor_dfs = [
        (tstay_cstay_SSS_3col, 'tstay_cstay_SSS'),
        (tstay_cstay_SDD_3col, 'tstay_cstay_SDD'),
        (tstay_cstay_SNN_3col, 'tstay_cstay_SNN'),
        (tstay_cstay_DSD_3col, 'tstay_cstay_DSD'),
        (tstay_cstay_DNN_3col, 'tstay_cstay_DNN'),
        (tstay_cstay_DDD_3col, 'tstay_cstay_DDD'),
        (tstay_cstay_DDS_3col, 'tstay_cstay_DDS'),
        (tstay_cswitch_SSS_3col, 'tstay_cswitch_SSS'),
        (tstay_cswitch_SDD_3col, 'tstay_cswitch_SDD'),
        (tstay_cswitch_SNN_3col, 'tstay_cswitch_SNN'),
        (tstay_cswitch_DSD_3col, 'tstay_cswitch_DSD'),
        (tstay_cswitch_DNN_3col, 'tstay_cswitch_DNN'),
        (tstay_cswitch_DDD_3col, 'tstay_cswitch_DDD'),
        (tstay_cswitch_DDS_3col, 'tstay_cswitch_DDS'),
        (tswitch_cswitch_SSS_3col, 'tswitch_cswitch_SSS'),
        (tswitch_cswitch_SDD_3col, 'tswitch_cswitch_SDD'),
        (tswitch_cswitch_SNN_3col, 'tswitch_cswitch_SNN'),
        (tswitch_cswitch_DSD_3col, 'tswitch_cswitch_DSD'),
        (tswitch_cswitch_DNN_3col, 'tswitch_cswitch_DNN'),
        (tswitch_cswitch_DDD_3col, 'tswitch_cswitch_DDD'),
        (tswitch_cswitch_DDS_3col, 'tswitch_cswitch_DDS'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            tstay_cstay_SSS,
            tstay_cstay_SDD,
            tstay_cstay_SNN,
            tstay_cstay_DSD,
            tstay_cstay_DNN,
            tstay_cstay_DDD,
            tstay_cstay_DDS,
            tstay_cswitch_SSS,
            tstay_cswitch_SDD,
            tstay_cswitch_SNN,
            tstay_cswitch_DSD,
            tstay_cswitch_DNN,
            tstay_cswitch_DDD,
            tstay_cswitch_DDS,
            tswitch_cswitch_SSS,
            tswitch_cswitch_SDD,
            tswitch_cswitch_SNN,
            tswitch_cswitch_DSD,
            tswitch_cswitch_DNN,
            tswitch_cswitch_DDD,
            tswitch_cswitch_DDS,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "tstay_cstay_SSS": "tstay_cstay_SSS",
        "tstay_cstay_SDD": "tstay_cstay_SDD",
        "tstay_cstay_SNN": "tstay_cstay_SNN",
        "tstay_cstay_DSD": "tstay_cstay_DSD",
        "tstay_cstay_DNN": "tstay_cstay_DNN",
        "tstay_cstay_DDD": "tstay_cstay_DDD",
        "tstay_cstay_DDS": "tstay_cstay_DDS",
        "tstay_cswitch_SSS": "tstay_cswitch_SSS",
        "tstay_cswitch_SDD": "tstay_cswitch_SDD",
        "tstay_cswitch_SNN": "tstay_cswitch_SNN",
        "tstay_cswitch_DSD": "tstay_cswitch_DSD",
        "tstay_cswitch_DNN": "tstay_cswitch_DNN",
        "tstay_cswitch_DDD": "tstay_cswitch_DDD",
        "tstay_cswitch_DDS": "tstay_cswitch_DDS",
        "tswitch_cswitch_SSS": "tswitch_cswitch_SSS",
        "tswitch_cswitch_SDD": "tswitch_cswitch_SDD",
        "tswitch_cswitch_SNN": "tswitch_cswitch_SNN",
        "tswitch_cswitch_DSD": "tswitch_cswitch_DSD",
        "tswitch_cswitch_DNN": "tswitch_cswitch_DNN",
        "tswitch_cswitch_DDD": "tswitch_cswitch_DDD",
        "tswitch_cswitch_DDS": "tswitch_cswitch_DDS",
        #spatialTS cue switch cost while shapeMatching is "off"
        "(tstay_cswitch_SNN+tstay_cswitch_DNN)-(tstay_cstay_SNN+tstay_cstay_DNN)": "1/2*(tstay_cswitch_SNN+tstay_cswitch_DNN)-1/2*(tstay_cstay_SNN+tstay_cstay_DNN)",
        #spatialTS task switch cost while shapeMatching is "off"
        "(tswitch_cswitch_SNN+tswitch_cswitch_DNN)-(tstay_cswitch_SNN+tstay_cswitch_DNN)": "1/2*(tswitch_cswitch_SNN+tswitch_cswitch_DNN)-1/2*(tstay_cswitch_SNN+tstay_cswitch_DNN)",
        #main vars while spatialTS is "off"
        "(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS)-(tstay_cstay_SNN+tstay_cstay_DNN)": "1/3*(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS)-1/2*(tstay_cstay_SNN+tstay_cstay_DNN)",
        #spatialTS cue switch cost across all other shapeMatching trial types
        "(tstay_cswitch_SSS+tstay_cswitch_SDD+tstay_cswitch_SNN+tstay_cswitch_DSD+tstay_cswitch_DNN+tstay_cswitch_DDD+tstay_cswitch_DDS)-(tstay_cstay_SSS+tstay_cstay_SDD+tstay_cstay_SNN+tstay_cstay_DSD+tstay_cstay_DNN+tstay_cstay_DDD+tstay_cstay_DDS)":
        "1/7*(tstay_cswitch_SSS+tstay_cswitch_SDD+tstay_cswitch_SNN+tstay_cswitch_DSD+tstay_cswitch_DNN+tstay_cswitch_DDD+tstay_cswitch_DDS)-1/7*(tstay_cstay_SSS+tstay_cstay_SDD+tstay_cstay_SNN+tstay_cstay_DSD+tstay_cstay_DNN+tstay_cstay_DDD+tstay_cstay_DDS)",
        #spatialTS task switch cost across all other shapeMatching trial types
        "(tswitch_cswitch_SSS+tswitch_cswitch_SDD+tswitch_cswitch_SNN+tswitch_cswitch_DSD+tswitch_cswitch_DNN+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-(tstay_cswitch_SSS+tstay_cswitch_SDD+tstay_cswitch_SNN+tstay_cswitch_DSD+tstay_cswitch_DNN+tstay_cswitch_DDD+tstay_cswitch_DDS)":
        "1/7*(tswitch_cswitch_SSS+tswitch_cswitch_SDD+tswitch_cswitch_SNN+tswitch_cswitch_DSD+tswitch_cswitch_DNN+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-1/7*(tstay_cswitch_SSS+tstay_cswitch_SDD+tstay_cswitch_SNN+tstay_cswitch_DSD+tstay_cswitch_DNN+tstay_cswitch_DDD+tstay_cswitch_DDS)",
        #main vars across all other spatialTS trial types
        "(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS+tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS+tswitch_cswitch_SDD+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-(tstay_cstay_SNN+tstay_cstay_DNN+tstay_cswitch_SNN+tstay_cswitch_DNN+tswitch_cswitch_SNN+tswitch_cswitch_DNN)":
        "1/9*(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS+tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS+tswitch_cswitch_SDD+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-1/6*(tstay_cstay_SNN+tstay_cstay_DNN+tstay_cswitch_SNN+tstay_cswitch_DNN+tswitch_cswitch_SNN+tswitch_cswitch_DNN)",
        #interaction for cue switch cost
        "((tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS)-(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS))-((tstay_cswitch_SNN+tstay_cswitch_DNN)-(tstay_cstay_SNN+tstay_cstay_DNN))":
        "1/3*(tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS)-1/3*(tstay_cstay_SDD+tstay_cstay_DDD+tstay_cstay_DDS)-1/2*(tstay_cswitch_SNN+tstay_cswitch_DNN)+1/2*(tstay_cstay_SNN+tstay_cstay_DNN)",
        #interaction for task switch cost
        "((tswitch_cswitch_SDD+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-(tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS))-((tswitch_cswitch_SNN+tswitch_cswitch_DNN)-(tstay_cswitch_SNN+tstay_cswitch_DNN))":
        "1/3*(tswitch_cswitch_SDD+tswitch_cswitch_DDD+tswitch_cswitch_DDS)-1/3*(tstay_cswitch_SDD+tstay_cswitch_DDD+tstay_cswitch_DDS)-1/2*(tswitch_cswitch_SNN+tswitch_cswitch_DNN)+1/2*(tstay_cswitch_SNN+tstay_cswitch_DNN)",
        #task - baseline
        "task-baseline": "1/21*(tstay_cstay_SSS+tstay_cstay_SDD+tstay_cstay_SNN+tstay_cstay_DSD+tstay_cstay_DNN+tstay_cstay_DDD+tstay_cstay_DDS+" +
                        "tstay_cswitch_SSS+tstay_cswitch_SDD+tstay_cswitch_SNN+tstay_cswitch_DSD+tstay_cswitch_DNN+tstay_cswitch_DDD+tstay_cswitch_DDS+" +
                        "tswitch_cswitch_SSS+tswitch_cswitch_SDD+tswitch_cswitch_SNN+tswitch_cswitch_DSD+tswitch_cswitch_DNN+tswitch_cswitch_DDD+tswitch_cswitch_DDS)",
        }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_nBackWShapeMatching_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    """Creates basic nBack + shapeMatching regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    """
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "nBackWShapeMatching")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="rt_fast",
    )

    match_td_same_1back, match_td_same_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_same_1back" and key_press == correct_response and response_time >=0.2',
        demean_amp=False,
        cond_id="match_td_same_1back",
    )
    match_td_same_2back, match_td_same_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_same_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_td_same_2back",
    )
    match_td_diff_1back, match_td_diff_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_diff_1back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_td_diff_1back",
    )
    match_td_diff_2back, match_td_diff_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_diff_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_td_diff_2back",
    )
    match_td_na_1back, match_td_na_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_na_1back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_td_na_1back",
    )
    match_td_na_2back, match_td_na_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_td_na_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_td_na_2back",
    )
    mismatch_td_same_1back, mismatch_td_same_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_same_1back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_same_1back",
    )
    mismatch_td_same_2back, mismatch_td_same_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_same_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_same_2back",
    )
    mismatch_td_diff_1back, mismatch_td_diff_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_diff_1back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_diff_1back",
    )
    mismatch_td_diff_2back, mismatch_td_diff_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_diff_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_diff_2back",
    )
    mismatch_td_na_1back, mismatch_td_na_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_na_1back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_na_1back",
    )
    mismatch_td_na_2back, mismatch_td_na_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_td_na_2back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_td_na_2back",
    )

    regressor_dfs = [
        (match_td_same_1back_3col, 'match_td_same_1back'),
        (match_td_same_2back_3col, 'match_td_same_2back'),
        (match_td_diff_1back_3col, 'match_td_diff_1back'),
        (match_td_diff_2back_3col, 'match_td_diff_2back'),
        (match_td_na_1back_3col, 'match_td_na_1back'),
        (match_td_na_2back_3col, 'match_td_na_2back'),
        (mismatch_td_same_1back_3col, 'mismatch_td_same_1back'),
        (mismatch_td_same_2back_3col, 'mismatch_td_same_2back'),
        (mismatch_td_diff_1back_3col, 'mismatch_td_diff_1back'),
        (mismatch_td_diff_2back_3col, 'mismatch_td_diff_2back'),
        (mismatch_td_na_1back_3col, 'mismatch_td_na_1back'),
        (mismatch_td_na_2back_3col, 'mismatch_td_na_2back'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            match_td_same_1back,
            match_td_same_2back,
            match_td_diff_1back,
            match_td_diff_2back,
            match_td_na_1back,
            match_td_na_2back,
            mismatch_td_same_1back,
            mismatch_td_same_2back,
            mismatch_td_diff_1back,
            mismatch_td_diff_2back,
            mismatch_td_na_1back,
            mismatch_td_na_2back,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "match_td_same_1back": "match_td_same_1back",
        "match_td_same_2back": "match_td_same_2back",
        "match_td_diff_1back": "match_td_diff_1back",
        "match_td_diff_2back": "match_td_diff_2back",
        "match_td_na_1back": "match_td_na_1back",
        "match_td_na_2back": "match_td_na_2back",
        "mismatch_td_same_1back": "mismatch_td_same_1back",
        "mismatch_td_same_2back": "mismatch_td_same_2back",
        "mismatch_td_diff_1back": "mismatch_td_diff_1back",
        "mismatch_td_diff_2back": "mismatch_td_diff_2back",
        "mismatch_td_na_1back": "mismatch_td_na_1back",
        "mismatch_td_na_2back": "mismatch_td_na_2back",
        #2back-1back when shapeMatching is "off"
        "(match_td_na_2back+mismatch_td_na_2back)-(match_td_na_1back+mismatch_td_na_1back)":
        "1/2*(match_td_na_2back+mismatch_td_na_2back)-1/2*(match_td_na_1back+mismatch_td_na_1back)",
        #main vars when nBack is "off"
        "(match_td_diff_1back+mismatch_td_diff_1back)-(match_td_na_1back+mismatch_td_na_1back)": "1/2*(match_td_diff_1back+mismatch_td_diff_1back)-1/2*(match_td_na_1back+mismatch_td_na_1back)",
        #2back-1back across all shapeMatching trial types
        "(match_td_same_2back+match_td_diff_2back+match_td_na_2back+mismatch_td_same_2back+mismatch_td_diff_2back+mismatch_td_na_2back)-(match_td_same_1back+match_td_diff_1back+match_td_na_1back+mismatch_td_same_1back+mismatch_td_diff_1back+mismatch_td_na_1back)":
        "1/6*(match_td_same_2back+match_td_diff_2back+match_td_na_2back+mismatch_td_same_2back+mismatch_td_diff_2back+mismatch_td_na_2back)-1/6*(match_td_same_1back+match_td_diff_1back+match_td_na_1back+mismatch_td_same_1back+mismatch_td_diff_1back+mismatch_td_na_1back)",
        #main vars across all other nBack trial types
        "(match_td_diff_2back+match_td_diff_1back+mismatch_td_diff_2back+mismatch_td_diff_1back)-(match_td_na_2back+match_td_na_1back+mismatch_td_na_2back+mismatch_td_na_1back)":
        "1/4*(match_td_diff_2back+match_td_diff_1back+mismatch_td_diff_2back+mismatch_td_diff_1back)-1/4*(match_td_na_2back+match_td_na_1back+mismatch_td_na_2back+mismatch_td_na_1back)",
        #interaction
        "((match_td_diff_2back+mismatch_td_diff_2back)-(match_td_na_2back+mismatch_td_na_2back))-((match_td_diff_1back+mismatch_td_diff_1back)-(match_td_na_1back+mismatch_td_na_1back))":
        "1/2*(match_td_diff_2back+mismatch_td_diff_2back)-1/2*(match_td_na_2back+mismatch_td_na_2back)-1/2*(match_td_diff_1back+mismatch_td_diff_1back)+1/2*(match_td_na_1back+mismatch_td_na_1back)",
        #task - baseline
        "task-baseline": "1/12*(match_td_same_1back+match_td_same_2back+match_td_diff_1back+match_td_diff_2back+match_td_na_1back+match_td_na_2back+" +
                        "mismatch_td_same_1back+mismatch_td_same_2back+mismatch_td_diff_1back+mismatch_td_diff_2back+mismatch_td_na_1back+mismatch_td_na_2back)",
        }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_nBackWSpatialTS_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    '''Creates basic nBack + spatialTS regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    '''
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "nBackWSpatialTS")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="rt_fast",
    )

    #make all cells lowercase
    events_df["trial_type"] = events_df["trial_type"].str.lower()

    mismatch_tstay_cstay_1back, mismatch_tstay_cstay_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tstay_cstay" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tstay_cstay_1back",
    )
    mismatch_tstay_cswitch_1back, mismatch_tstay_cswitch_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tstay_cswitch" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tstay_cswitch_1back",
    )
    mismatch_tswitch_cswitch_1back, mismatch_tswitch_cswitch_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tswitch_cswitch" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tswitch_cswitch_1back",
    )
    match_tstay_cstay_1back, match_tstay_cstay_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tstay_cstay" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tstay_cstay_1back",
    )
    match_tstay_cswitch_1back, match_tstay_cswitch_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tstay_cswitch" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tstay_cswitch_1back",
    )
    match_tswitch_cswitch_1back, match_tswitch_cswitch_1back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tswitch_cswitch" and task == "1-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tswitch_cswitch_1back",
    )
    mismatch_tstay_cstay_2back, mismatch_tstay_cstay_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tstay_cstay" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tstay_cstay_2back",
    )
    mismatch_tstay_cswitch_2back, mismatch_tstay_cswitch_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tstay_cswitch" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tstay_cswitch_2back",
    )
    mismatch_tswitch_cswitch_2back, mismatch_tswitch_cswitch_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "mismatch_tswitch_cswitch" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="mismatch_tswitch_cswitch_2back",
    )
    match_tstay_cstay_2back, match_tstay_cstay_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tstay_cstay" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tstay_cstay_2back",
    )
    match_tstay_cswitch_2back, match_tstay_cswitch_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tstay_cswitch" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tstay_cswitch_2back",
    )
    match_tswitch_cswitch_2back, match_tswitch_cswitch_2back_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "match_tswitch_cswitch" and task == "2-back" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="match_tswitch_cswitch_2back",
    )
    regressor_dfs = [
        (mismatch_tstay_cstay_1back_3col, 'mismatch_tstay_cstay_1back'),
        (mismatch_tstay_cswitch_1back_3col, 'mismatch_tstay_cswitch_1back'),
        (mismatch_tswitch_cswitch_1back_3col, 'mismatch_tswitch_cswitch_1back'),
        (match_tstay_cstay_1back_3col, 'match_tstay_cstay_1back'),
        (match_tstay_cswitch_1back_3col, 'match_tstay_cswitch_1back'),
        (match_tswitch_cswitch_1back_3col, 'match_tswitch_cswitch_1back'),
        (mismatch_tstay_cstay_2back_3col, 'mismatch_tstay_cstay_2back'),
        (mismatch_tstay_cswitch_2back_3col, 'mismatch_tstay_cswitch_2back'),
        (mismatch_tswitch_cswitch_2back_3col, 'mismatch_tswitch_cswitch_2back'),
        (match_tstay_cstay_2back_3col, 'match_tstay_cstay_2back'),
        (match_tstay_cswitch_2back_3col, 'match_tstay_cswitch_2back'),
        (match_tswitch_cswitch_2back_3col, 'match_tswitch_cswitch_2back'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            mismatch_tstay_cstay_1back,
            mismatch_tstay_cswitch_1back,
            mismatch_tswitch_cswitch_1back,
            match_tstay_cstay_1back,
            match_tstay_cswitch_1back,
            match_tswitch_cswitch_1back,
            mismatch_tstay_cstay_2back,
            mismatch_tstay_cswitch_2back,
            mismatch_tswitch_cswitch_2back,
            match_tstay_cstay_2back,
            match_tstay_cswitch_2back,
            match_tswitch_cswitch_2back,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "mismatch_tstay_cstay_1back": "mismatch_tstay_cstay_1back",
        "mismatch_tstay_cswitch_1back": "mismatch_tstay_cswitch_1back",
        "mismatch_tswitch_cswitch_1back": "mismatch_tswitch_cswitch_1back",
        "match_tstay_cstay_1back": "match_tstay_cstay_1back",
        "match_tstay_cswitch_1back": "match_tstay_cswitch_1back",
        "match_tswitch_cswitch_1back": "match_tswitch_cswitch_1back",
        "mismatch_tstay_cstay_2back": "mismatch_tstay_cstay_2back",
        "mismatch_tstay_cswitch_2back": "mismatch_tstay_cswitch_2back",
        "mismatch_tswitch_cswitch_2back": "mismatch_tswitch_cswitch_2back",
        "match_tstay_cstay_2back": "match_tstay_cstay_2back",
        "match_tstay_cswitch_2back": "match_tstay_cswitch_2back",
        "match_tswitch_cswitch_2back": "match_tswitch_cswitch_2back",
        #2back-1back when spatialTS is "off"
        "(match_tstay_cstay_2back+mismatch_tstay_cstay_2back)-(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)":
        "1/2*(match_tstay_cstay_2back+mismatch_tstay_cstay_2back)-1/2*(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)",
        #cue switch cost when nBack is "off"
        "(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)":
        "1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-1/2*(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)",
        #task switch cost when nBack is "off"
        "(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)":
        "1/2*(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)",
        #2back-1back across all spatialTS trial types
        "(match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back+mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back)-(match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back)":
        "1/6*(match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back+mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back)-1/6*(match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back)",
        #cue switch cost across all other nBack trial types
        "(match_tstay_cswitch_1back+match_tstay_cswitch_2back+mismatch_tstay_cswitch_1back+mismatch_tstay_cswitch_2back)-(match_tstay_cstay_1back+match_tstay_cstay_2back+mismatch_tstay_cstay_1back+mismatch_tstay_cstay_2back)":
        "1/4*(match_tstay_cswitch_1back+match_tstay_cswitch_2back+mismatch_tstay_cswitch_1back+mismatch_tstay_cswitch_2back)-1/4*(match_tstay_cstay_1back+match_tstay_cstay_2back+mismatch_tstay_cstay_1back+mismatch_tstay_cstay_2back)",
        #task switch cost across all other nBack trial types
        "(match_tswitch_cswitch_1back+match_tswitch_cswitch_2back+mismatch_tswitch_cswitch_1back+mismatch_tswitch_cswitch_2back)-(match_tstay_cswitch_1back+match_tstay_cswitch_2back+mismatch_tstay_cswitch_1back+mismatch_tstay_cswitch_2back)":
        "1/4*(match_tswitch_cswitch_1back+match_tswitch_cswitch_2back+mismatch_tswitch_cswitch_1back+mismatch_tswitch_cswitch_2back)-1/4*(match_tstay_cswitch_1back+match_tstay_cswitch_2back+mismatch_tstay_cswitch_1back+mismatch_tstay_cswitch_2back)",
        #cue switch cost interaction
        "((match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back)-(match_tstay_cstay_2back+mismatch_tstay_cstay_2back))-((match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-(match_tstay_cstay_1back+mismatch_tstay_cstay_1back))":
        "(1/2*(match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back)-1/2*(match_tstay_cstay_2back+mismatch_tstay_cstay_2back))-(1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-1/2*(match_tstay_cstay_1back+mismatch_tstay_cstay_1back))",
        #task switch cost interaction
        "((match_tswitch_cswitch_2back+mismatch_tswitch_cswitch_2back)-(match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back))-((match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back))":
        "(1/2*(match_tswitch_cswitch_2back+mismatch_tswitch_cswitch_2back)-1/2*(match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back))-(1/2*(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back))",
        #task - baseline
        "task-baseline": "1/12*(mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back+match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back+match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back)",
        }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

def make_basic_directedForgettingWCuedTS_desmat(
    events_file,
    duration_choice,
    add_deriv,
    regress_rt,
    mean_rt,
    n_scans,
    tr,
    confound_regressors,
    model_break
):
    '''Creates basic directedForgetting + cuedTS regressors (and derivatives),
    defining error regressors and adding fmriprep confound regressors
       Input
         events_df: events data frame (events.tsv data)
         n_scans: Number of scans
         tr: time resolution
         confound_regressors: Confounds derived from fmriprep output
       Returns
          design_matrix: pd data frame including all regressors (and derivatives)
          contrasts: dictionary of contrasts in nilearn friendly format
          rt_subset: Boolean for extracting correct rows of events_df in the case that
              rt regressors are requeset.
    '''
    events_df = pd.read_csv(events_file, sep="\t", dtype={'response_time': float})
    (
        events_df["junk_trials"],
        events_df["omission"],
        events_df["commission"],
        events_df["rt_fast"],
    ) = define_nuisance_trials(events_df, "directedForgettingWCuedTS")
    percent_junk = np.mean(events_df["junk_trials"])
    events_df["constant_1_column"] = 1

    omission_regressor, omission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="omission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="omission",
    )
    commission_regressor, commission_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="commission",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="commission",
    )
    rt_fast, rt_fast_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="rt_fast",
        duration_column="constant_1_column",
        subset='trial_type != "n/a"',
        demean_amp=False,
        cond_id="rt_fast",
    )

    neg_tswitch_cswitch, neg_tswitch_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "neg_tswitch_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="neg_tswitch_cswitch",
    )
    neg_tstay_cswitch, neg_tstay_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "neg_tstay_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="neg_tstay_cswitch",
    )
    neg_tstay_cstay, neg_tstay_cstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "neg_tstay_cstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="neg_tstay_cstay",
    )
    pos_tswitch_cswitch, pos_tswitch_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "pos_tswitch_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="pos_tswitch_cswitch",
    )
    pos_tstay_cswitch, pos_tstay_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "pos_tstay_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="pos_tstay_cswitch",
    )
    pos_tstay_cstay, pos_tstay_cstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "pos_tstay_cstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="pos_tstay_cstay",
    )
    con_tswitch_cswitch, con_tswitch_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "con_tswitch_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="con_tswitch_cswitch",
    )
    con_tstay_cswitch, con_tstay_cswitch_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "con_tstay_cswitch" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="con_tstay_cswitch",
    )
    con_tstay_cstay, con_tstay_cstay_3col = make_regressor_and_derivative(
        n_scans=n_scans,
        tr=tr,
        events_df=events_df,
        add_deriv=add_deriv,
        amplitude_column="constant_1_column",
        duration_column="constant_1_column",
        subset='trial_type == "con_tstay_cstay" and key_press == correct_response and response_time >= 0.2',
        demean_amp=False,
        cond_id="con_tstay_cstay",
    )
    regressor_dfs = [
        (neg_tswitch_cswitch_3col, 'neg_tswitch_cswitch'),
        (neg_tstay_cswitch_3col, 'neg_tstay_cswitch'),
        (neg_tstay_cstay_3col, 'neg_tstay_cstay'),
        (pos_tswitch_cswitch_3col, 'pos_tswitch_cswitch'),
        (pos_tstay_cswitch_3col, 'pos_tstay_cswitch'),
        (pos_tstay_cstay_3col, 'pos_tstay_cstay'),
        (con_tswitch_cswitch_3col, 'con_tswitch_cswitch'),
        (con_tstay_cswitch_3col, 'con_tstay_cswitch'),
        (con_tstay_cstay_3col, 'con_tstay_cstay'),
        (omission_3col, 'omission'),
        (commission_3col, 'commission'),
        (rt_fast_3col, 'rt_fast'),
    ]
    design_matrix = pd.concat(
        [
            neg_tswitch_cswitch,
            neg_tstay_cswitch,
            neg_tstay_cstay,
            pos_tswitch_cswitch,
            pos_tstay_cswitch,
            pos_tstay_cstay,
            con_tswitch_cswitch,
            con_tstay_cswitch,
            con_tstay_cstay,
            omission_regressor,
            commission_regressor,
            rt_fast,
            confound_regressors,
        ],
        axis=1,
    )
    if model_break:
        break_period, break_period_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="constant_1_column",
            duration_column="duration",
            subset='trial_id == "break_with_performance_feedback"',
            demean_amp=False,
            cond_id="break_period",
        )
        design_matrix = pd.concat([design_matrix, break_period], axis=1)
        regressor_dfs.append((break_period_3col, 'break_period'))
    simplified_events_df = create_simplified_events_df(regressor_dfs)

    contrasts = {
        #each trial type - baseline
        "neg_tswitch_cswitch": "neg_tswitch_cswitch",
        "neg_tstay_cswitch": "neg_tstay_cswitch",
        "neg_tstay_cstay": "neg_tstay_cstay",
        "pos_tswitch_cswitch": "pos_tswitch_cswitch",
        "pos_tstay_cswitch": "pos_tstay_cswitch",
        "pos_tstay_cstay": "pos_tstay_cstay",
        "con_tswitch_cswitch": "con_tswitch_cswitch",
        "con_tstay_cswitch": "con_tstay_cswitch",
        "con_tstay_cstay": "con_tstay_cstay",
        #cue switch cost while directedForgetting is "off"
        "con_tstay_cswitch-con_tstay_cstay": "con_tstay_cswitch-con_tstay_cstay",
        #task switch cost while directedForgetting is "off"
        "con_tswitch_cswitch-con_tstay_cswitch": "con_tswitch_cswitch-con_tstay_cswitch",
        #directedForgetting contrast while cuedTS is "off"
        "neg_tstay_cstay-con_tstay_cstay": "neg_tstay_cstay-con_tstay_cstay",
        #cue switch cost across all DF conditions
        "(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)-(neg_tstay_cstay+pos_tstay_cstay+con_tstay_cstay)":
        "1/3*(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)-1/3*(neg_tstay_cstay+pos_tstay_cstay+con_tstay_cstay)",
        #task switch cost across all DF conditions
        "(neg_tswitch_cswitch+pos_tswitch_cswitch+con_tswitch_cswitch)-(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)":
        "1/3*(neg_tswitch_cswitch+pos_tswitch_cswitch+con_tswitch_cswitch)-1/3*(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)",
        #directedForgetting contrast across all cuedTS conditions
        "(neg_tstay_cstay+neg_tstay_cswitch+neg_tswitch_cswitch)-(con_tstay_cstay+con_tstay_cswitch+con_tswitch_cswitch)":
        "1/3*(neg_tstay_cstay+neg_tstay_cswitch+neg_tswitch_cswitch)-1/3*(con_tstay_cstay+con_tstay_cswitch+con_tswitch_cswitch)",
        #cue switch cost interaction
        "(neg_tstay_cswitch-con_tstay_cswitch)-(neg_tstay_cstay-con_tstay_cstay)": "1/2*(neg_tstay_cswitch-con_tstay_cswitch)-1/2*(neg_tstay_cstay-con_tstay_cstay)",
        #task switch cost interaction
        "(neg_tswitch_cswitch-con_tswitch_cswitch)-(neg_tstay_cswitch-con_tstay_cswitch)": "1/2*(neg_tswitch_cswitch-con_tswitch_cswitch)-1/2*(neg_tstay_cswitch-con_tstay_cswitch)",
        #task - baseline
        "task-baseline": "1/9*(neg_tswitch_cswitch+neg_tstay_cswitch+neg_tstay_cstay+pos_tswitch_cswitch+pos_tstay_cswitch+pos_tstay_cstay+con_tswitch_cswitch+con_tstay_cswitch+con_tstay_cstay)",
        }
    if regress_rt == "rt_centered":
        events_df["response_time_centered"] = events_df.response_time - mean_rt
        rt, rt_3col = make_regressor_and_derivative(
            n_scans=n_scans,
            tr=tr,
            events_df=events_df,
            add_deriv=add_deriv,
            amplitude_column="response_time_centered",
            duration_column="constant_1_column",
            subset="trial_id == 'test_trial' and trial_type != 'n/a' and key_press == correct_response and response_time >= 0.2",
            demean_amp=False,
            cond_id="response_time",
        )
        design_matrix = pd.concat([design_matrix, rt], axis=1)
        contrasts["response_time"] = "response_time"
    return design_matrix, contrasts, percent_junk, simplified_events_df

make_task_desmat_fcn_dict = {
    "cuedTS": make_basic_cuedTS_desmat,
    "directedForgetting": make_basic_directedForgetting_desmat,
    "flanker": make_basic_flanker_desmat,
    "goNogo": make_basic_goNogo_desmat,
    "nBack": make_basic_nBack_desmat,
    "shapeMatching": make_basic_shapeMatching_desmat,
    "spatialTS": make_basic_spatialTS_desmat,
    "stopSignal": make_basic_stopSignal_desmat,
    "directedForgettingWFlanker": make_basic_directedForgettingWFlanker_desmat,
    "stopSignalWDirectedForgetting": make_basic_stopSignalWDirectedForgetting_desmat,
    "stopSignalWFlanker": make_basic_stopSignalWFlanker_desmat,
    "spatialTSWCuedTS": make_basic_spatialTSWCuedTS_desmat,
    "flankerWShapeMatching": make_basic_flankerWShapeMatching_desmat,
    "cuedTSWFlanker": make_basic_cuedTSWFlanker_desmat,
    "spatialTSWShapeMatching": make_basic_spatialTSWShapeMatching_desmat,
    "nBackWShapeMatching": make_basic_nBackWShapeMatching_desmat,
    "nBackWSpatialTS": make_basic_nBackWSpatialTS_desmat,
    "directedForgettingWCuedTS": make_basic_directedForgettingWCuedTS_desmat
}
