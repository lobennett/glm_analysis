# Define regressor configurations
regressor_config = {
    "cuedTS": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'tn/a_cn/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'tn/a_cn/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'tn/a_cn/a'",
        },
        "n/a": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "trial_type == 'tn/a_cn/a'",
        },
        "task_stay_cue_switch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "key_press == correct_response and response_time >= 0.2 "
                     "and trial_type == 'tstay_cswitch'",
        },
        "task_stay_cue_stay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "key_press == correct_response and response_time >= 0.2 "
                     "and trial_type == 'tstay_cstay'",
        },
        "task_switch_cue_switch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "key_press == correct_response and response_time >= 0.2 "
                     "and trial_type == 'tswitch_cswitch'",
        }
    }
}
