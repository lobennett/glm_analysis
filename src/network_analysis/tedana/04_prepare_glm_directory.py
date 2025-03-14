from pathlib import Path
from glob import glob
import shutil
import pandas as pd
import numpy as np
import os

def preprocess_events(df):
    df['trial_type'].fillna('na', inplace=True)
    df['onset'] = df['onset'] - 7 * 1.49 
    neg_rt = df['response_time'] < 0
    df['junk'] = np.where(neg_rt, 1, 0)
    df['na_trials'] = np.where((df['trial_type']=='na'), 1, 0)
    df['response_time'] = np.where(neg_rt, np.nan, df['response_time'])
    return df

def main():
    bids_dir = Path("./data/fMRI_data/")
    subj_id = "s1273"
    task_name = "cuedTS"

    # Directories from which we will move data
    subj_bids_dir = Path(bids_dir, f'sub-{subj_id}')
    subj_fmriprep_dir = Path(subj_bids_dir, "derivatives/fmriprep")
    subj_tedana_dir = Path("./data/tedana_transformed", f'sub-{subj_id}')

    # Directories to which we will move data
    glm_dir = Path("./data/glm_data", f'sub-{subj_id}')
    glm_dir.mkdir(parents=True, exist_ok=True)

    # Copy over all masks and confounds files 
    t1w_masks = sorted(glob(subj_fmriprep_dir / "ses-*" / "func" / f"*T1w*brain_mask.nii.gz"))
    mni_masks = sorted(glob(subj_fmriprep_dir / "ses-*" / "func" / f"*MNI*brain_mask.nii.gz"))
    confounds = sorted(glob(subj_fmriprep_dir / "ses-*" / "func" / f"*confounds*.tsv"))
    events = sorted(glob(subj_bids_dir / "ses-*" / "func" / f"*events.tsv"))

    # Move all the above files to the glm_dir
    for file in t1w_masks + mni_masks + confounds:
        rel_path = os.path.relpath(file, start=subj_bids_dir if file in events else subj_fmriprep_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file, dest_path)

    for file in events:
        # Process the events file
        df = pd.read_csv(file, sep='\t')
        df = preprocess_events(df)
        # Write out preprocessed events file
        rel_path = os.path.relpath(file, start=subj_bids_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        df.to_csv(dest_path, sep='\t', index=False)

    # Copy over all bold files 
    bold_files = sorted(glob(subj_tedana_dir / "ses-*" / "func" / f"*desc-optcom_bold.nii.gz"))

    # Copy over all bold files 
    for file in bold_files:
        rel_path = os.path.relpath(file, start=subj_tedana_dir)
        dest_path = glm_dir / rel_path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file, dest_path)

    return

if __name__ == "__main__":
    main()



# import glob
# import pandas as pd
# import shutil
# import numpy as np
# import os

# bids = '/oak/stanford/groups/russpold/data/network_grant/validation_BIDS_old/'
# fmriprep = bids+'derivatives/fmriprep/'
# glm_dir = bids+'derivatives/glm_data/'
# tedana = bids+'derivatives/tedana_kundu/'
# # bids = '/oak/stanford/groups/russpold/data/network_grant/discovery_BIDS_21.0.1/'
# # fmriprep = bids+'derivatives/fmriprep_21.0.1_c/'
# # tedana = bids+'derivatives/tedana_kundu_c/'
# # glm_dir = bids+'derivatives/glm_data_MNI/'
# os.makedirs(glm_dir, exist_ok=True)
# subjects = glob.glob(glm_dir+'sub-*')
# subjects = [sub.split('/')[-1] for sub in subjects]
# for sub in subjects:
#     mni_mask = glob.glob(fmriprep+f'*{sub}/*/*/*task-*MNI*brain_mask.nii.gz')
#     for mask in mni_mask:
#         new_file = mask.replace(fmriprep, glm_dir)
#         os.makedirs(os.path.dirname(new_file), exist_ok=True)
#         shutil.copyfile(mask, new_file)
#     confounds = sorted(glob.glob(fmriprep+f'*{sub}/*/*/*confounds*.tsv'))
#     print("Confound files count: ", len(confounds))
#     for file in confounds:
#         df = pd.read_csv(file, sep='\t')
#         df = df.iloc[7:]
#         new_file = file.replace(fmriprep, glm_dir)
#         os.makedirs(os.path.dirname(new_file), exist_ok=True)
#         df.to_csv(new_file, sep='\t')

#     events = sorted(glob.glob(bids+f'*{sub}/*/func/*events.tsv'))
#     print("Event files count: ", len(events))
#     for file in events:
#         df = pd.read_csv(file, sep='\t')
#         df['trial_type'].fillna('na', inplace=True)
#         df['onset'] = df['onset']-7*1.49
#         neg_rt = df['response_time'] < 0
#         df['junk'] = np.where(neg_rt, 1, 0)
#         df['na_trials'] = np.where((df['trial_type']=='na'), 1, 0)
#         df['response_time'] = np.where(neg_rt, np.nan, df['response_time'])
#         new_file = file.replace(bids, glm_dir)
#         os.makedirs(os.path.dirname(new_file), exist_ok=True)
#         df.to_csv(new_file, sep='\t', index=False)

    # masks = sorted(glob.glob(fmriprep+f'*{sub}/*/*/*T1w*brain_mask.nii.gz'))
    # print("Mask files count: ", len(masks))
    # for file in masks:
    #     new_file = file.replace(fmriprep, glm_dir)
    #     os.makedirs(os.path.dirname(new_file), exist_ok=True)
    #     shutil.copyfile(file, new_file)

    # bolds = sorted(glob.glob(tedana+f'*{sub}/*/desc-optcom_bold.nii.gz'))
    #bolds = sorted(glob.glob(tedana+f'*{sub}/*/desc-optcomDenoised_bold.nii.gz'))
