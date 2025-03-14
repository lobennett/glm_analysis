#!/bin/bash
#
#SBATCH -J fmriprep
#SBATCH --time=2-00:00:00
#SBATCH -n 1
#SBATCH --array 1 # TODO: Change this to the number of subjects
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=16G
#SBATCH -p russpold,hns,normal 
# Outputs ----------------------------------
#SBATCH -o ./log/%x-%A-%a.out
#SBATCH -e ./log/%x-%A-%a.err
#SBATCH --mail-user=logben@stanford.edu
#SBATCH --mail-type=END
# ------------------------------------------


: '

Name: fmriprep.sbatch

Description: This script runs fmriprep on a dataset. 

Usage: sbatch ./batch/fmriprep.sbatch

Notes: 

'

# Prepare computing environment
source ./batch/setup_env.sh

# Prepare some writeable bind-mount points.
mkdir -p $FMRIPREP_DERIVS_DIR
mkdir -p $FMRIPREP_WORK_DIR

# Prepare binds
APPTAINER_CMD="apptainer run --cleanenv -B $BIDS_DIR:/data -B $FMRIPREP_WORK_DIR:/work -B $FS_DIR:/fsdir ${FMRIPREP_VERSION}"

# Parse the subs.txt file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed "${SLURM_ARRAY_TASK_ID}q;d" ${SUBJECTS_FILE} )

# Compose the command line
cmd="${APPTAINER_CMD} /data ${FMRIPREP_DERIVS_DIR} participant --participant-label $subject -w /work --nthreads 8 --mem_mb 85000 --output-spaces MNI152NLin2009cAsym:res-2 func anat --me-output-echos --fs-license-file $FS_LICENSE --verbose"

# Setup done, run the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd
exitcode=$?

# Output results to a table
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode