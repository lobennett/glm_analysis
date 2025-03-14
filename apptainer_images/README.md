# Apptainer Images

Directory containing apptainer images for fMRIPrep, MRIQC, and QSIPrep.

fMRIPrep: `docker pull nipreps/fmriprep:latest` 
MRIQC: `docker pull poldracklab/mriqc:latest` 
QSIPrep: `docker pull pennlinc/qsiprep:latest` 

I recommend timestamping the images to improve reproducibility.

For example, `docker pull fmriprep_latest_20250313.sif nipreps/fmriprep:latest`

You can also pull the images using the batch script `batch/pull_images.sbatch`.