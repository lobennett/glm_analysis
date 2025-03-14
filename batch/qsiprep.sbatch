#!/bin/bash
#SBATCH -J qsiprep
#SBATCH --time=12:00:00
#SBATCH -n 1
#SBATCH --array 1 # List of subject IDs
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH -p russpold,hns,normal
# Outputs ----------------------------------
#SBATCH -o ./log/%x-%A-%a.out
#SBATCH -e ./log/%x-%A-%a.err 
#SBATCH --mail-user=logben@stanford.edu
#SBATCH --mail-type=END 
# ------------------------------------------

: '
Name: qsiprep.sbatch

Description: This script runs qsiprep on a dataset. 

Usage: sbatch ./batch/qsiprep.sbatch

Notes: 
'

# Prepare computing environment
source ./batch/setup_env.sh

# Prepare apptainer/singularity command line
APPTAINER_CMD="apptainer run --cleanenv -B $BIDS_DIR:/data -B $WORK_DIR:/work $APPTAINER_IMAGE"

# Compose subject ID for each array task
SUBJECT=$( sed "${SLURM_ARRAY_TASK_ID}q;d" ${SUBJECTS_FILE} )

# Compose the command line with flags for fMRIPrep
cmd="$APPTAINER_CMD /data $DERIVS_DIR participant --participant-label $SUBJECT -w /work --output-resolution 1.5 --distortion-group-merge concat --skip-bids-validation --verbose"

# Show and execute the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd 
exitcode=$? # store exit code

echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode 
