# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "setuptools",
#     "tedana",
# ]
# ///
from glob import glob
from pathlib import Path
import json
import os
from tedana.workflows import tedana_workflow
import logging

def get_echo_metadata(files):
    echo_dict = {}
    default_times_by_echo_num = {1: 13.4, 2: 36.4, 3: 59.4}
    for file in files:
        with open(file, "r") as f:
            data = json.load(f)
        basename = os.path.basename(file)
        split_basename = basename.split("_echo-")
        echo_num = int(split_basename[1].replace('_bold.json', ''))
        echo_time = data.get("EchoTime", default_times_by_echo_num.get(echo_num, None))

        assert echo_time is not None, f"Echo time is none for {file}"

        echo_dict[echo_num] = echo_time

    return list(echo_dict.values())

def get_sub_ses_task(f):
    components = f.name.split('_')

    # Extract each component
    ses = next((comp for comp in components if comp.startswith('ses-')), None)
    task_name = next((comp for comp in components if comp.startswith('task-')), None)
    run_number = next((comp for comp in components if comp.startswith('run-')), None)

    return ses, task_name, run_number

def group_files(files):
    file_groups = {}
    for f in files:
        ses, task_name, run_number = get_sub_ses_task(f)
        key = (ses, task_name, run_number)
        if key not in file_groups:
            file_groups[key] = []
        file_groups[key].append(f)
    return file_groups


def main():
    bids_dir = Path("./data/fMRI_data/")
    subj_id = "s1273"
    logging.basicConfig(level=logging.INFO)

    subj_bids_dir = Path(f"{bids_dir}/sub-{subj_id}")
    subj_tedana_dir = Path(f"./data/tedana_dummy_removed/sub-{subj_id}")
    outdir = Path("./data/tedana_denoised") / f"sub-{subj_id}"
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Group files by session, task, and run
    file_groups = group_files(subj_tedana_dir.glob("*bold.nii.gz"))
    
    # Process each group
    for (ses, task_name, run_number), files in file_groups.items():
        if len(files) != 3:
            raise ValueError(f"Expected 3 echo files, found {len(files)} for {ses} {task_name} {run_number}")
            
        print(f"Processing {ses} {task_name} {run_number} with {len(files)} echo files")

        json_file_pattern = subj_bids_dir / ses / "func" / f"*{subj_id}*{ses}*{task_name}*{run_number}*.json"
        json_files = glob(str(json_file_pattern))
        echo_values = get_echo_metadata(json_files)
        
        outbase = f"sub-{subj_id}_{ses}_{task_name}_{run_number}_rec-tedana"
        outpath = outdir / outbase

        datafiles = [str(f) for f in files]
        logging.info(f"Running tedana on {outbase}")
        tedana_workflow(
            datafiles,
            echo_values,
            out_dir=outpath,
            tedpca="kundu",
        )

        # break

if __name__ == "__main__":
    main()
