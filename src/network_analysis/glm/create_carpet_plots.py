import os
from glob import glob
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nf
import numpy as np
import pandas as pd
import seaborn as sns
from nilearn import masking
from nilearn.masking import apply_mask


def extract_session_from_filename(filename):
    return (
        filename.split('_ses-')[1].split('_')[0] if '_ses-' in filename else 'unknown'
    )

def get_task_baseline_contrasts(task_name):
    contrasts = {
        "cuedTS": (
            "1/3*(task_stay_cue_switch+task_stay_cue_stay+task_switch_cue_switch)"
        ),
        "spatialTS": (
            "1/3*(task_stay_cue_switch+task_stay_cue_stay+task_switch_cue_switch)"
        ),
        "directedForgetting": "1/4*(con+pos+neg+memory_and_cue)",
        "flanker": "1/2*congruent + 1/2*incongruent",
        "goNogo": "1/2*go+1/2*nogo_success",
        "nBack": "1/4*(mismatch_1back+match_1back+mismatch_2back+match_2back)",
        "stopSignal": "1/3*go + 1/3*stop_failure + 1/3*stop_success",
        "shapeMatching": "1/7*(SSS+SDD+SNN+DSD+DDD+DDS+DNN)",
        "directedForgettingWFlanker": (
            "1/7*(congruent_pos+congruent_neg+congruent_con+incongruent_pos+"
            "incongruent_neg+incongruent_con+memory_and_cue)"
        ),
        "stopSignalWDirectedForgetting": (
            "1/10*(go_pos+go_neg+go_con+stop_success_pos+stop_success_neg+"
            "stop_success_con+stop_failure_pos+stop_failure_neg+stop_failure_con+"
            "memory_and_cue)"
        ),
        "stopSignalWFlanker": (
            "1/6*(go_congruent+go_incongruent+stop_success_congruent+"
            "stop_success_incongruent+stop_failure_congruent+stop_failure_incongruent)"
        )
    }
    return contrasts[task_name]

def get_target_contrast(contrast, task_name):
    contrasts = {
        'task-baseline': get_task_baseline_contrasts(task_name),
        'main_vars': "1/3*(SDD+DDD+DDS)-1/2*(SNN+DNN)",
        'cue_switch_cost': "task_stay_cue_switch-task_stay_cue_stay",
        'task_switch_cost': "task_switch_cue_switch-task_stay_cue_switch"
    }
    return contrasts.get(contrast, contrast)

def main():
    # get unique contrast names
    indiv_contrasts_dir = Path("./results/indiv_contrasts")
    quality_control_dir = Path("./results/quality_control")
    subject = "s1273"
    task = "cuedTS"

    print(f"{indiv_contrasts_dir}/*{subject}*{task}*effect-size*")
    all_contrasts = glob(f"{indiv_contrasts_dir}/*{subject}*{task}*effect-size*")
    contrasts = [
        contrast.split('_contrast-')[1].split('_rtmodel')[0]
        for contrast in all_contrasts
    ]
    unique_contrasts = np.unique(contrasts)

    # carefully concatenate contrasts and variance images to keep order consistent
    all_eff_sizes = []
    all_eff_vars = []
    all_con_names = []
    all_sessions = []
    all_vifs = []

    for contrast in unique_contrasts:
        contrast_effect_size = glob(
            f'{indiv_contrasts_dir}/*{subject}*{task}*contrast-{contrast}_rtmodel*effect-size*'
        )
        contrast_effect_var = [
            eff_size.replace('effect-size', 'stat-variance')
            for eff_size in contrast_effect_size
        ]

        # Extract session numbers from filenames
        sessions = []

        for eff_size in contrast_effect_size:
            # Extract session from filename (format: ses-XX)
            # - Session
            session_match = extract_session_from_filename(eff_size)
            sessions.append(session_match)

            # LOAD VIFS
            vif_file = list(
                quality_control_dir.glob(f"*{subject}*{session_match}*{task}*")
            )
            assert len(vif_file) == 1, f"Expected 1 VIF file, found {len(vif_file)}"
            vif_data = pd.read_csv(vif_file[0])
            target_contrast = get_target_contrast(contrast, task)
            vif_value = vif_data[
                vif_data['contrast'] == target_contrast
            ]['VIF'].values[0]
            all_vifs.append(vif_value)

        all_eff_sizes.extend(contrast_effect_size)
        all_eff_vars.extend(contrast_effect_var)
        all_con_names.extend([contrast]*len(contrast_effect_size))
        all_sessions.extend(sessions)

    # prep data and mask
    eff_size_4d = nf.funcs.concat_images(all_eff_sizes)
    eff_size_4d_array = eff_size_4d.get_fdata()

    mask_img = masking.compute_epi_mask(eff_size_4d)

    # get min/max for colorbar (feel free to change)
    # We're mosty interested in finding outliers, so we don't really need to see the
    # full range of values
    # i.e., there will be a lot of gray in the image and those voxels are fine as they
    # will not be outliers
    data_nonzero = eff_size_4d_array[eff_size_4d_array.nonzero()]
    cutoff_max = np.quantile(data_nonzero, .9)
    cutoff_min = np.quantile(data_nonzero, .1)

    # Apply mask and plot
    data = apply_mask(eff_size_4d, mask_img)

    # Sort data by contrast name and then by session number
    # Create a list of tuples with (contrast, session, index)
    sort_indices = [
        (con, int(ses), i)
        for i, (con, ses) in enumerate(zip(all_con_names, all_sessions))
    ]
    # Sort by contrast first, then by session number as integer
    sort_indices.sort(key=lambda x: (x[0], x[1]))
    # Get the original indices in the sorted order
    sorted_indices = [i for _, _, i in sort_indices]

    # Reorder data and labels
    sorted_data = data[sorted_indices]
    sorted_con_names = [all_con_names[i] for i in sorted_indices]
    sorted_sessions = [all_sessions[i] for i in sorted_indices]
    sorted_vifs = [all_vifs[i] for i in sorted_indices]

    plt.figure(figsize=(20, 10))
    plt.subplots_adjust(left=0.3)
    sns.heatmap(
        sorted_data, cmap='coolwarm', center=0, vmin=cutoff_min, vmax=cutoff_max
    )
    plt.xticks([], [])
    plt.xlabel('Voxels')

    # Create combined labels with contrast, session, and VIF value
    combined_labels = [
        f"{con} (ses-{ses}) (VIF={vif:.2f})"
        for con, ses, vif in zip(sorted_con_names, sorted_sessions, sorted_vifs)
    ]

    plt.yticks(
        ticks=np.arange(len(combined_labels)), labels=combined_labels, rotation=0
    )
    plt.ylabel('Contrasts')
    plt.title(f'Effect sizes ({subject})')
    outdir = f'./figures/{subject}/{task}/carpet_plots/'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(f'{outdir}/{subject}_{task}_effect_sizes.png')
    print(f"Saved {subject}_{task}_effect_sizes.png to {outdir}")
    plt.close()



if __name__ == "__main__":
    main()
