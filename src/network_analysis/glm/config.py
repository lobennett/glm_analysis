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
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'tstay_cswitch'"
            ),
        },
        "task_stay_cue_stay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'tstay_cstay'"
            ),
        },
        "task_switch_cue_switch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'tswitch_cswitch'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type != 'tn/a_cn/a' and trial_id == 'test_trial'"
            ),
        }
    },
    "directedForgetting": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "memory_and_cue": {
            "amplitude_column": "constant_1_column",
            "duration_column": "duration",
            "subset": 'trial_id == "test_stim" or trial_id == "test_cue"',
        },
        "con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "con"'
            ),
        },
        "pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "pos"'
            ),
        },
        "neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "neg"'
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_id == 'test_trial'"
            ),
        }
    },
    "flanker": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "congruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type =='congruent'"
            ),
        },
        "incongruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type =='incongruent'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_id == 'test_trial'"
            ),
        }
    },
    "goNogo": {
        "go_omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "nogo_failure": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "trial_type == 'nogo_failure'",
        },
        "go": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go'"
            ),
        },
        "nogo_success": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "trial_type == 'nogo_success'",
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go'"
            ),
        }
    },
    "nBack": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "mismatch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'mismatch' and delay == 1"
            ),
        },
        "match_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'match' and delay == 1"
            ),
        },
        "mismatch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'mismatch' and delay == 2"
            ),
        },
        "match_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'match' and delay == 2"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type != 'n/a'"
            ),
        }
    },
    "stopSignal": {
        "go_omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go'"
            ),
        },
        "stop_success": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "trial_type == 'stop_success'",
        },
        "stop_failure": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": "trial_type == 'stop_failure'",
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go'"
            ),
        }
    },
    "shapeMatching": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "SSS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'SSS'"
            ),
        },
        "SDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'SDD'"
            ),
        },
        "SNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'SNN'"
            ),
        },
        "DSD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'DSD'"
            ),
        },
        "DNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'DNN'"
            ),
        },
        "DDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'DDD'"
            ),
        },
        "DDS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'DDS'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_id == 'test_trial'"
            ),
        }
    },
    "spatialTS": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "mismatch_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cstay" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cswitch" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tswitch_cswitch" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cstay" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cswitch" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tswitch_cswitch" and task == "1-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tstay_cstay_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cstay" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tstay_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cswitch" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tswitch_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tswitch_cswitch" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tstay_cstay_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cstay" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tstay_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cswitch" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tswitch_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tswitch_cswitch" and task == "2-back" '
                'and key_press == correct_response and response_time >= 0.2'
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' "
                "and key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "directedForgettingWCuedTS": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": 'trial_type != "n/a"',
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": 'trial_type != "n/a"',
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": 'trial_type != "n/a"',
        },
        "neg_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "neg_tswitch_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "neg_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "neg_tstay_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "neg_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "neg_tstay_cstay" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "pos_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "pos_tswitch_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "pos_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "pos_tstay_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "pos_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "pos_tstay_cstay" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "con_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "con_tswitch_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "con_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "con_tstay_cswitch" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "con_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "con_tstay_cstay" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "directedForgettingWFlanker": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "memory_and_cue": {
            "amplitude_column": "constant_1_column",
            "duration_column": "duration",
            "subset": 'trial_id == "test_stim" or trial_id == "test_cue"',
        },
        "congruent_pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "congruent_pos"'
            ),
        },
        "congruent_neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "congruent_neg"'
            ),
        },
        "congruent_con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "congruent_con"'
            ),
        },
        "incongruent_pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "incongruent_pos"'
            ),
        },
        "incongruent_neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "incongruent_neg"'
            ),
        },
        "incongruent_con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'key_press == correct_response and response_time >= 0.2 '
                'and trial_type == "incongruent_con"'
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_id == 'test_trial'"
            ),
        }
    },
    "stopSignalWDirectedForgetting": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go_pos'"
            ),
        },
        "go_neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go_neg'"
            ),
        },
        "go_con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go_con'"
            ),
        },
        "stop_success_pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_success_pos'"
            ),
        },
        "stop_success_neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_success_neg'"
            ),
        },
        "stop_success_con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_success_con'"
            ),
        },
        "stop_failure_pos": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_failure_pos'"
            ),
        },
        "stop_failure_neg": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_failure_neg'"
            ),
        },
        "stop_failure_con": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_failure_con'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type.isin(['go_pos', 'go_neg', 'go_con'])"
            ),
        }
    },
    "stopSignalWFlanker": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "go_congruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "co  nstant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go_congruent'"
            ),
        },
        "go_incongruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type == 'go_incongruent'"
            ),
        },
        "stop_success_congruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_success_congruent'"
            ),
        },
        "stop_success_incongruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_success_incongruent'"
            ),
        },
        "stop_failure_congruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_failure_congruent'"
            ),
        },
        "stop_failure_incongruent": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'stop_failure_incongruent'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 "
                "and trial_type.isin(['go_congruent', 'go_incongruent'])"
            ),
        }
    },
    "spatialTSWCuedTS": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "match_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cstay" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tstay_cswitch" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "match_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "match_tswitch_cswitch" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cstay" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tstay_cswitch" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "mismatch_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "mismatch_tswitch_cswitch" and task == "1-back" and '
                'key_press == correct_response and response_time >= 0.2'
            ),
        },
        "task_stay_cue_stay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "tstay_cstay" and key_press == correct_response and '
                'response_time >= 0.2'
            ),
        },
        "task_stay_cue_switch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "tstay_cswitch" and key_press == correct_response and '
                'response_time >= 0.2'
            ),
        },
        "task_switch_cue_switch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                'trial_type == "tswitch_cswitch" and key_press == correct_response and '
                'response_time >= 0.2'
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "flankerWShapeMatching": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": None,
        },
        "congruent_SSS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_SSS'"
            ),
        },
        "congruent_SDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_SDD'"
            ),
        },
        "congruent_SNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_SNN'"
            ),
        },
        "congruent_DSD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_DSD'"
            ),
        },
        "congruent_DDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_DDD'"
            ),
        },
        "congruent_DDS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_DDS'"
            ),
        },
        "congruent_DNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'congruent_DNN'"
            ),
        },
        "incongruent_SSS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_SSS'"
            ),
        },
        "incongruent_SDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_SDD'"
            ),
        },
        "incongruent_SNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_SNN'"
            ),
        },
        "incongruent_DSD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_DSD'"
            ),
        },
        "incongruent_DDD": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_DDD'"
            ),
        },
        "incongruent_DDS": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_DDS'"
            ),
        },
        "incongruent_DNN": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_type == 'incongruent_DNN'"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "key_press == correct_response and response_time >= 0.2 and "
                "trial_id == 'test_trial'"
            ),
        }
    },
    "cuedTSWFlanker": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "congruent_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'congruent_tstay_cstay' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "congruent_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'congruent_tstay_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "congruent_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'congruent_tswitch_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "incongruent_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'incongruent_tstay_cstay' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "incongruent_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'incongruent_tstay_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "incongruent_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'incongruent_tswitch_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "spatialTSWShapeMatching": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "SSS_match_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'SSS_match_tstay_cstay' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "SSS_match_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'SSS_match_tstay_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "SSS_match_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'SSS_match_tswitch_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "DDD_match_tstay_cstay": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'DDD_match_tstay_cstay' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "DDD_match_tstay_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'DDD_match_tstay_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "DDD_match_tswitch_cswitch": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'DDD_match_tswitch_cswitch' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "nBackWShapeMatching": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "match_SSS_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_SSS' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_DDD_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_DDD' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_SSS_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_SSS' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_DDD_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_DDD' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_SSS_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_SSS' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_DDD_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_DDD' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_SSS_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_SSS' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_DDD_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_DDD' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    },
    "nBackWSpatialTS": {
        "omission": {
            "amplitude_column": "omission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "commission": {
            "amplitude_column": "commission",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "rt_fast": {
            "amplitude_column": "rt_fast",
            "duration_column": "constant_1_column",
            "subset": "trial_type != 'n/a'",
        },
        "match_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tstay_cstay' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tstay_cswitch' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tswitch_cswitch' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tstay_cstay_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tstay_cstay' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tstay_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tstay_cswitch' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tswitch_cswitch_1back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tswitch_cswitch' and delay == 1 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_tstay_cstay_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tstay_cstay' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_tstay_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tstay_cswitch' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "match_tswitch_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'match_tswitch_cswitch' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tstay_cstay_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tstay_cstay' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tstay_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tstay_cswitch' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "mismatch_tswitch_cswitch_2back": {
            "amplitude_column": "constant_1_column",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_type == 'mismatch_tswitch_cswitch' and delay == 2 and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        },
        "response_time": {
            "amplitude_column": "response_time_centered",
            "duration_column": "constant_1_column",
            "subset": (
                "trial_id == 'test_trial' and trial_type != 'n/a' and "
                "key_press == correct_response and response_time >= 0.2"
            ),
        }
    }
}

contrasts_config = {
    "cuedTS": {
        "task_switch_cost": "task_switch_cue_switch-task_stay_cue_switch",
        "cue_switch_cost": "task_stay_cue_switch-task_stay_cue_stay",
        "task_switch_cue_switch-task_stay_cue_stay": (
            "task_switch_cue_switch-task_stay_cue_stay"
        ),
        "task-baseline": (
            "1/3*(task_stay_cue_switch+task_stay_cue_stay+"
            "task_switch_cue_switch)"
        ),
        "response_time": "response_time"
    },
    "directedForgetting": {
        "neg-con": "neg-con",
        "task-baseline": "1/4*(con+pos+neg+memory_and_cue)",
        "response_time": "response_time"
    },
    "flanker": {
        "incongruent-congruent": "incongruent-congruent",
        "task-baseline": "1/2*congruent + 1/2*incongruent",
        "response_time": "response_time"
    },
    "goNogo": {
        "go": "go",
        "nogo_success": "nogo_success",
        "nogo_success-go": "nogo_success-go",
        "task-baseline": "1/2*go+1/2*nogo_success",
        "response_time": "response_time"
    },
    "nBack": {
        "twoBack-oneBack": (
            "1/2*(mismatch_2back+match_2back-mismatch_1back-match_1back)"
        ),
        "match-mismatch": (
            "1/2*(match_2back+match_1back-mismatch_2back-mismatch_1back)"
        ),
        "task-baseline": (
            "1/4*(mismatch_1back+match_1back+mismatch_2back+match_2back)"
        ),
        "response_time": "response_time"
    },
    "stopSignal": {
        "go": "go",
        "stop_success": "stop_success",
        "stop_failure": "stop_failure",
        "stop_success-go": "stop_success-go",
        "stop_failure-go": "stop_failure-go",
        "stop_success-stop_failure": "stop_success-stop_failure",
        "stop_failure-stop_success": "stop_failure-stop_success",
        "task-baseline": "1/3*go + 1/3*stop_failure + 1/3*stop_success",
        "response_time": "response_time"
    },
    "shapeMatching": {
        "task-baseline": "1/7*(SSS+SDD+SNN+DSD+DDD+DDS+DNN)",
        "main_vars": "1/3*(SDD+DDD+DDS)-1/2*(SNN+DNN)",
        "SSS": "SSS",
        "SDD": "SDD",
        "SNN": "SNN",
        "DSD": "DSD",
        "DDD": "DDD",
        "DDS": "DDS",
        "DNN": "DNN",
        "response_time": "response_time"
    },
    "spatialTS": {
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
        "task-baseline": (
            "1/12*("
            "mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back+"
            "match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+"
            "mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back+"
            "match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back"
            ")"
        ),
        "(match_tstay_cstay_2back+mismatch_tstay_cstay_2back)-"
        "(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)": (
            "1/2*(match_tstay_cstay_2back+mismatch_tstay_cstay_2back)-"
            "1/2*(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)"
        ),
        "(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-"
        "(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)": (
            "1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)-"
            "1/2*(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)"
        ),
        "(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-"
        "(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)": (
            "1/2*(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)-"
            "1/2*(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)"
        ),
        "response_time": "response_time"
    },
    "directedForgettingWCuedTS": {
        "neg_tswitch_cswitch": "neg_tswitch_cswitch",
        "neg_tstay_cswitch": "neg_tstay_cswitch",
        "neg_tstay_cstay": "neg_tstay_cstay",
        "pos_tswitch_cswitch": "pos_tswitch_cswitch",
        "pos_tstay_cswitch": "pos_tstay_cswitch",
        "pos_tstay_cstay": "pos_tstay_cstay",
        "con_tswitch_cswitch": "con_tswitch_cswitch",
        "con_tstay_cswitch": "con_tstay_cswitch",
        "con_tstay_cstay": "con_tstay_cstay",
        "con_tstay_cswitch-con_tstay_cstay": "con_tstay_cswitch-con_tstay_cstay",
        "con_tswitch_cswitch-con_tstay_cswitch": (
            "con_tswitch_cswitch-con_tstay_cswitch"
        ),
        "neg_tstay_cstay-con_tstay_cstay": "neg_tstay_cstay-con_tstay_cstay",
        "(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)-"
        "(neg_tstay_cstay+pos_tstay_cstay+con_tstay_cstay)": (
            "1/3*(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)-"
            "1/3*(neg_tstay_cstay+pos_tstay_cstay+con_tstay_cstay)"
        ),
        "(neg_tswitch_cswitch+pos_tswitch_cswitch+con_tswitch_cswitch)-"
        "(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)": (
            "1/3*(neg_tswitch_cswitch+pos_tswitch_cswitch+con_tswitch_cswitch)-"
            "1/3*(neg_tstay_cswitch+pos_tstay_cswitch+con_tstay_cswitch)"
        ),
        "(neg_tstay_cstay+neg_tstay_cswitch+neg_tswitch_cswitch)-"
        "(con_tstay_cstay+con_tstay_cswitch+con_tswitch_cswitch)": (
            "1/3*(neg_tstay_cstay+neg_tstay_cswitch+neg_tswitch_cswitch)-"
            "1/3*(con_tstay_cstay+con_tstay_cswitch+con_tswitch_cswitch)"
        ),
        "(neg_tstay_cswitch-con_tstay_cswitch)-"
        "(neg_tstay_cstay-con_tstay_cstay)": (
            "1/2*(neg_tstay_cswitch-con_tstay_cswitch)-"
            "1/2*(neg_tstay_cstay-con_tstay_cstay)"
        ),
        "(neg_tswitch_cswitch-con_tswitch_cswitch)-"
        "(neg_tstay_cswitch-con_tstay_cswitch)": (
            "1/2*(neg_tswitch_cswitch-con_tswitch_cswitch)-"
            "1/2*(neg_tstay_cswitch-con_tstay_cswitch)"
        ),
        "task-baseline": (
            "1/9*("
            "neg_tswitch_cswitch+neg_tstay_cswitch+neg_tstay_cstay+"
            "pos_tswitch_cswitch+pos_tstay_cswitch+pos_tstay_cstay+"
            "con_tswitch_cswitch+con_tstay_cswitch+con_tstay_cstay"
            ")"
        ),
        "response_time": "response_time"
    },
    "directedForgettingWFlanker": {
        "incongruent-congruent": (
            "1/3*(incongruent_pos+incongruent_neg+incongruent_con)-"
            "1/3*(congruent_pos+congruent_neg+congruent_con)"
        ),
        "pos-con": (
            "1/2*(congruent_pos+incongruent_pos)-"
            "1/2*(congruent_con+incongruent_con)"
        ),
        "neg-con": (
            "1/2*(congruent_neg+incongruent_neg)-"
            "1/2*(congruent_con+incongruent_con)"
        ),
        "task-baseline": (
            "1/7*("
            "congruent_pos+congruent_neg+congruent_con+"
            "incongruent_pos+incongruent_neg+incongruent_con+memory_and_cue"
            ")"
        ),
        "response_time": "response_time"
    },
    "stopSignalWDirectedForgetting": {
        "go_pos-go_con": "go_pos-go_con",
        "go_neg-go_con": "go_neg-go_con",
        "stop_success-go": (
            "1/3*(stop_success_pos+stop_success_neg+stop_success_con)-"
            "1/3*(go_pos+go_neg+go_con)"
        ),
        "stop_failure-go": (
            "1/3*(stop_failure_pos+stop_failure_neg+stop_failure_con)-"
            "1/3*(go_pos+go_neg+go_con)"
        ),
        "stop_success-stop_failure": (
            "1/3*(stop_success_pos+stop_success_neg+stop_success_con)-"
            "1/3*(stop_failure_pos+stop_failure_neg+stop_failure_con)"
        ),
        "task-baseline": (
            "1/9*("
            "go_pos+go_neg+go_con+"
            "stop_success_pos+stop_success_neg+stop_success_con+"
            "stop_failure_pos+stop_failure_neg+stop_failure_con"
            ")"
        ),
        "response_time": "response_time"
    },
    "stopSignalWFlanker": {
        "go_incongruent-go_congruent": "go_incongruent-go_congruent",
        "stop_success-go": (
            "1/2*(stop_success_congruent+stop_success_incongruent)-"
            "1/2*(go_congruent+go_incongruent)"
        ),
        "stop_failure-go": (
            "1/2*(stop_failure_congruent+stop_failure_incongruent)-"
            "1/2*(go_congruent+go_incongruent)"
        ),
        "stop_success-stop_failure": (
            "1/2*(stop_success_congruent+stop_success_incongruent)-"
            "1/2*(stop_failure_congruent+stop_failure_incongruent)"
        ),
        "task-baseline": (
            "1/6*("
            "go_congruent+go_incongruent+"
            "stop_success_congruent+stop_success_incongruent+"
            "stop_failure_congruent+stop_failure_incongruent"
            ")"
        ),
        "response_time": "response_time"
    },
    "spatialTSWCuedTS": {
        "match_tstay_cstay_1back": "match_tstay_cstay_1back",
        "match_tstay_cswitch_1back": "match_tstay_cswitch_1back",
        "match_tswitch_cswitch_1back": "match_tswitch_cswitch_1back",
        "mismatch_tstay_cstay_1back": "mismatch_tstay_cstay_1back",
        "mismatch_tstay_cswitch_1back": "mismatch_tstay_cswitch_1back",
        "mismatch_tswitch_cswitch_1back": "mismatch_tswitch_cswitch_1back",
        "task_stay_cue_stay": "task_stay_cue_stay",
        "task_stay_cue_switch": "task_stay_cue_switch",
        "task_switch_cue_switch": "task_switch_cue_switch",
        "task-baseline": (
            "1/9*("
            "match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+"
            "mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back+"
            "task_stay_cue_stay+task_stay_cue_switch+task_switch_cue_switch"
            ")"
        ),
        "response_time": "response_time"
    },
    "flankerWShapeMatching": {
        "incongruent-congruent": (
            "1/7*("
            "incongruent_SSS+incongruent_SDD+incongruent_SNN+incongruent_DSD+"
            "incongruent_DDD+incongruent_DDS+incongruent_DNN"
            ")-1/7*("
            "congruent_SSS+congruent_SDD+congruent_SNN+congruent_DSD+"
            "congruent_DDD+congruent_DDS+congruent_DNN"
            ")"
        ),
        "task-baseline": (
            "1/14*("
            "congruent_SSS+congruent_SDD+congruent_SNN+congruent_DSD+"
            "congruent_DDD+congruent_DDS+congruent_DNN+"
            "incongruent_SSS+incongruent_SDD+incongruent_SNN+incongruent_DSD+"
            "incongruent_DDD+incongruent_DDS+incongruent_DNN"
            ")"
        ),
        "response_time": "response_time"
    },
    "cuedTSWFlanker": {
        "incongruent-congruent": (
            "1/3*(incongruent_tstay_cstay+incongruent_tstay_cswitch+incongruent_tswitch_cswitch)-"
            "1/3*(congruent_tstay_cstay+congruent_tstay_cswitch+congruent_tswitch_cswitch)"
        ),
        "tstay_cswitch-tstay_cstay": (
            "1/2*(congruent_tstay_cswitch+incongruent_tstay_cswitch)-"
            "1/2*(congruent_tstay_cstay+incongruent_tstay_cstay)"
        ),
        "tswitch_cswitch-tstay_cswitch": (
            "1/2*(congruent_tswitch_cswitch+incongruent_tswitch_cswitch)-"
            "1/2*(congruent_tstay_cswitch+incongruent_tstay_cswitch)"
        ),
        "task-baseline": (
            "1/6*("
            "congruent_tstay_cstay+congruent_tstay_cswitch+congruent_tswitch_cswitch+"
            "incongruent_tstay_cstay+incongruent_tstay_cswitch+incongruent_tswitch_cswitch"
            ")"
        ),
        "response_time": "response_time"
    },
    "spatialTSWShapeMatching": {
        "SSS-DDD": (
            "1/3*(SSS_match_tstay_cstay+SSS_match_tstay_cswitch+SSS_match_tswitch_cswitch)-"
            "1/3*(DDD_match_tstay_cstay+DDD_match_tstay_cswitch+DDD_match_tswitch_cswitch)"
        ),
        "tstay_cswitch-tstay_cstay": (
            "1/2*(SSS_match_tstay_cswitch+DDD_match_tstay_cswitch)-"
            "1/2*(SSS_match_tstay_cstay+DDD_match_tstay_cstay)"
        ),
        "tswitch_cswitch-tstay_cswitch": (
            "1/2*(SSS_match_tswitch_cswitch+DDD_match_tswitch_cswitch)-"
            "1/2*(SSS_match_tstay_cswitch+DDD_match_tstay_cswitch)"
        ),
        "task-baseline": (
            "1/6*("
            "SSS_match_tstay_cstay+SSS_match_tstay_cswitch+SSS_match_tswitch_cswitch+"
            "DDD_match_tstay_cstay+DDD_match_tstay_cswitch+DDD_match_tswitch_cswitch"
            ")"
        ),
        "response_time": "response_time"
    },
    "nBackWShapeMatching": {
        "twoBack-oneBack": (
            "1/4*("
            "match_SSS_2back+match_DDD_2back+mismatch_SSS_2back+mismatch_DDD_2back"
            ")-1/4*("
            "match_SSS_1back+match_DDD_1back+mismatch_SSS_1back+mismatch_DDD_1back"
            ")"
        ),
        "match-mismatch": (
            "1/4*("
            "match_SSS_1back+match_DDD_1back+match_SSS_2back+match_DDD_2back"
            ")-1/4*("
            "mismatch_SSS_1back+mismatch_DDD_1back+mismatch_SSS_2back+mismatch_DDD_2back"
            ")"
        ),
        "SSS-DDD": (
            "1/4*("
            "match_SSS_1back+mismatch_SSS_1back+match_SSS_2back+mismatch_SSS_2back"
            ")-1/4*("
            "match_DDD_1back+mismatch_DDD_1back+match_DDD_2back+mismatch_DDD_2back"
            ")"
        ),
        "task-baseline": (
            "1/8*("
            "match_SSS_1back+match_DDD_1back+mismatch_SSS_1back+mismatch_DDD_1back+"
            "match_SSS_2back+match_DDD_2back+mismatch_SSS_2back+mismatch_DDD_2back"
            ")"
        ),
        "response_time": "response_time"
    },
    "nBackWSpatialTS": {
        "twoBack-oneBack": (
            "1/6*("
            "match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back+"
            "mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back"
            ")-1/6*("
            "match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+"
            "mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back"
            ")"
        ),
        "match-mismatch": (
            "1/6*("
            "match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+"
            "match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back"
            ")-1/6*("
            "mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back+"
            "mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back"
            ")"
        ),
        "tstay_cswitch-tstay_cstay": (
            "1/4*("
            "(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)+"
            "(match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back)"
            ")-1/4*("
            "(match_tstay_cstay_1back+mismatch_tstay_cstay_1back)+"
            "(match_tstay_cstay_2back+mismatch_tstay_cstay_2back)"
            ")"
        ),
        "tswitch_cswitch-tstay_cswitch": (
            "1/4*("
            "(match_tswitch_cswitch_1back+mismatch_tswitch_cswitch_1back)+"
            "(match_tswitch_cswitch_2back+mismatch_tswitch_cswitch_2back)"
            ")-1/4*("
            "(match_tstay_cswitch_1back+mismatch_tstay_cswitch_1back)+"
            "(match_tstay_cswitch_2back+mismatch_tstay_cswitch_2back)"
            ")"
        ),
        "task-baseline": (
            "1/12*("
            "match_tstay_cstay_1back+match_tstay_cswitch_1back+match_tswitch_cswitch_1back+"
            "mismatch_tstay_cstay_1back+mismatch_tstay_cswitch_1back+mismatch_tswitch_cswitch_1back+"
            "match_tstay_cstay_2back+match_tstay_cswitch_2back+match_tswitch_cswitch_2back+"
            "mismatch_tstay_cstay_2back+mismatch_tstay_cswitch_2back+mismatch_tswitch_cswitch_2back"
            ")"
        ),
        "response_time": "response_time"
    }
}
