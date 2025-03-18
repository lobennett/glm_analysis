import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


def preprocess_events(df):
    df.fillna({'trial_type': 'na'}, inplace=True)
    df['onset'] = df['onset'] - 7 * 1.49
    neg_rt = df['response_time'] < 0
    df['junk'] = np.where(neg_rt, 1, 0)
    df['na_trials'] = np.where((df['trial_type']=='na'), 1, 0)
    df['response_time'] = np.where(neg_rt, np.nan, df['response_time'])
    return df

def preprocess_confounds(df):
    # Remove the first 7 TRs
    df = df.iloc[7:]
    return df.reset_index(drop=True)

def main():
    bids_dir = Path("./data/fMRI_data/")
    subj_id = "s1273"

    # Directories from which we will move data
    subj_bids_dir = Path(bids_dir, f'sub-{subj_id}')
    subj_fmriprep_dir = Path(bids_dir, f'derivatives/fmriprep/sub-{subj_id}')
    subj_tedana_dir = Path("./data/tedana_transformed", f'sub-{subj_id}')

    # Directories to which we will move data
    glm_dir = Path("./data/glm_data", f'sub-{subj_id}')
    glm_dir.mkdir(parents=True, exist_ok=True)

    # Copy over all masks and confounds files
    t1w_masks = sorted(subj_fmriprep_dir.glob("ses-*/func/*T1w*brain_mask.nii.gz"))
    mni_masks = sorted(subj_fmriprep_dir.glob("ses-*/func/*MNI*brain_mask.nii.gz"))
    confounds = sorted(subj_fmriprep_dir.glob("ses-*/func/*confounds*.tsv"))
    events = sorted(subj_bids_dir.glob("ses-*/func/*events.tsv"))

    # Move all the above files to the glm_dir
    # Process masks
    for file in t1w_masks + mni_masks:
        rel_path = os.path.relpath(file, start=subj_fmriprep_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file, dest_path)

    # Process confounds files
    for file in confounds:
        df = pd.read_csv(file, sep='\t')
        df = preprocess_confounds(df)
        rel_path = os.path.relpath(file, start=subj_fmriprep_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        df.to_csv(dest_path, sep='\t', index=False)

    # Process the events files
    for file in events:
        df = pd.read_csv(file, sep='\t')
        df = preprocess_events(df)
        # Write out preprocessed events file
        rel_path = os.path.relpath(file, start=subj_bids_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        df.to_csv(dest_path, sep='\t', index=False)

    # Copy over all bold files
    bold_files = sorted(subj_tedana_dir.glob("ses-*/func/*desc-optcom_bold.nii.gz"))
    for file in bold_files:
        rel_path = os.path.relpath(file, start=subj_tedana_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file, dest_path)

    return

if __name__ == "__main__":
    main()
