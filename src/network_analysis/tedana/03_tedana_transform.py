# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "nipype",
# ]
# ///
from pathlib import Path
import os
from nipype.interfaces.ants import ApplyTransforms

def get_sub_ses_task(f):
    components = f.split('_')
    # Extract each component
    for component in components:
        if component.startswith('ses-'):
            ses = component
        elif component.startswith('task-'):
            task_name = component
        elif component.startswith('run-'):
            run_number = component

    return ses, task_name, run_number


def apply_xforms(scan, outpath, xforms, reference):
    at = ApplyTransforms()
    at.inputs.input_image = scan
    at.inputs.reference_image = reference
    at.inputs.output_image = outpath
    at.inputs.interpolation = "LanczosWindowedSinc"
    at.inputs.transforms = xforms
    at.inputs.input_image_type = 3
    at.run()

def main() -> None:
    bids_dir = Path("./data/fMRI_data/")
    subj_id = "s1273"

    subj_fmriprep_dir = Path(bids_dir, f"derivatives/fmriprep/sub-{subj_id}")
    subj_tedana_dir = Path(f"./data/tedana_denoised/sub-{subj_id}")
    outdir = Path(f"./data/tedana_transformed/sub-{subj_id}")
    outdir.mkdir(parents=True, exist_ok=True)

    for f in subj_tedana_dir.glob('**/*optcom*.nii.gz'):
        basename = os.path.basename(str(f.parent))
        ses, task_name, run_number = get_sub_ses_task(basename)

        print(ses, task_name, run_number)

        fmriprep_ses_dir = subj_fmriprep_dir / ses / "func"

        bold_to_t1_xforms = list(fmriprep_ses_dir.glob(f"*{task_name}*from-boldref_to-T1w_mode-image_desc-coreg_xfm.txt"))
        bold_to_t1_space = list(fmriprep_ses_dir.glob(f"*{task_name}*space-T1w_boldref.nii.gz"))
        # bold_to_mni_space = list(fmriprep_ses_dir.glob(f"*{task_name}*space-MNI152NLin2009cAsym_res-2_boldref.nii.gz"))
        # t1w_to_mni_space = list(subj_fmriprep_dir.glob(f'ses-*/anat/*from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5'))

        # prepare outdirs
        outdir_full = outdir / ses / "func"
        outdir_full.mkdir(parents=True, exist_ok=True)

        # full outpath
        outpath = outdir_full / f"sub-{subj_id}_{ses}_{task_name}_{run_number}_space-T1w_desc-optcom_bold.nii.gz"

        if os.path.isfile(outpath):
            logging.warning(f"Skipping: {outpath} exists...")
            continue

        apply_xforms(
            scan=str(f),
            xforms=str(bold_to_t1_xforms[0]),
            outpath=str(outpath),
            reference=str(bold_to_t1_space[0]),
        )

        # return

if __name__ == "__main__":
    main()
