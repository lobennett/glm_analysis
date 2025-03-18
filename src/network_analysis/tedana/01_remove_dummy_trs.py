import logging
import os
from glob import glob
from pathlib import Path

import nibabel as nb
import pandas as pd


def check_dummy_trs(confounds_file):
    df = pd.read_csv(confounds_file, sep="\t")
    non_steady_cols = [col for col in df.columns if "non_steady_state_outlier" in col]
    return len(non_steady_cols)

def trim_will_cut_into_onset(event_file, n_dummy_trs):
    df = pd.read_csv(event_file, sep="\t")
    adjusted_onsets = df["onset"] - (1.49 * n_dummy_trs)
    # Create new df with adjusted onsets
    df_adjusted = df.copy()
    df_adjusted['onset'] = adjusted_onsets
    # Filter out rows where 'trial_id' starts with _fmri
    df_adjusted = df_adjusted[~df_adjusted['trial_id'].str.startswith('fmri_')]
    return df_adjusted["onset"].min() < 0

def trim_bold_file(bold_file, n_dummy_trs = 7):
    img = nb.load(bold_file)
    return img.slicer[:, :, :, n_dummy_trs:]

def main():
    bids_dir = Path("./data/fMRI_data/")
    subj_id = "s1273"

    logging.basicConfig(level=logging.INFO)

    subj_bids_dir = Path(bids_dir, f'sub-{subj_id}')
    subj_fmriprep_dir = Path(bids_dir, "derivatives/fmriprep", f'sub-{subj_id}')

    # Get all confounds files
    confounds_pattern = Path(subj_fmriprep_dir, "ses-*","func", f'sub-{subj_id}*timeseries.tsv')
    confounds_files = glob(str(confounds_pattern))

    amount_to_trim = {}
    for f in confounds_files:
        basename = Path(f).name.replace("_desc-confounds_timeseries.tsv", "")
        n_dummy_trs = check_dummy_trs(f)
        amount_to_trim[basename] = n_dummy_trs

    # Get all event files
    events_pattern = Path(subj_bids_dir, "ses-*", "func", f'sub-{subj_id}*events.tsv')
    events_files = glob(str(events_pattern))

    for file in events_files:
        basename = Path(file).name
        basename = basename.replace("_events.tsv", "")
        n_dummy_trs = amount_to_trim[basename]
        # - Right now, we are just trimming 7 TRs
        # - in the network code, this didn't actually throw an error
        # - but instead just logged things to console.
        # if trim_will_cut_into_onset(file, n_dummy_trs):
        #     raise ValueError(f"Removing {n_dummy_trs} TRs will cut into event onset in {file}")

    # Get all bold files
    bold_pattern = Path(subj_fmriprep_dir, "ses-*", "func", f'sub-{subj_id}*echo-*desc-preproc_bold.nii.gz')
    bold_files = glob(str(bold_pattern))

    # Create a local output directory
    outdir = Path("./data/tedana_dummy_removed") / f"sub-{subj_id}"
    os.makedirs(outdir, exist_ok=True)

    for f in bold_files:
        outname = Path(f).name.replace("_desc-preproc_bold.nii.gz", "_desc-preproc-dummyremoved_bold.nii.gz")
        basename = Path(f).name
        basename = basename.replace("_desc-preproc_bold.nii.gz", "").split('_echo')[0]
        logging.info(f"Removing {basename} TRs from {f}")

        n_dummy_trs = amount_to_trim[basename]
        outfile = outdir / outname

        if os.path.isfile(outfile):
            logging.warning(f"Skipping: {f} already exists...")
            continue

        # logging.info(f"Removing {n_dummy_trs} TRs from {f}")
        logging.info(f"Removing 7 TRs from {f}")

        # trimmed_img = trim_bold_file(f, n_dummy_trs)
        # - Right now, just trim 7 TRs although
        # - I think this should be based on the number
        # - of unstable TRs in the confounds file
        trimmed_img = trim_bold_file(f)

        # Save the file to the local output directory
        nb.save(trimmed_img, outfile)
        logging.info(f"Saved trimmed bold to {outfile}")

    return

if __name__ == "__main__":
    main()
