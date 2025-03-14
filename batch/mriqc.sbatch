#!/bin/bash
#
#SBATCH -J mriqc
#SBATCH --time=2-00:00:00
#SBATCH -n 1
#SBATCH --array 1 # TODO: Change this to the number of subjects
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH -p russpold,hns,normal
# Outputs ---------------------------------
#SBATCH -o ./log/%x-%A-%a.out
#SBATCH -e ./log/%x-%A-%a.err
#SBATCH --mail-user=logben@stanford.edu
#SBATCH --mail-type=END
# ------------------------------------------


: '

Name: mriqc.sbatch

Description: This script runs mriqc on a dataset. 

Usage: sbatch ./batch/mriqc.sbatch

Notes: 

'

# Prepare computing environment
source ./batch/setup_env.sh

# Prepare some writeable bind-mount points.
mkdir -p $MRIQC_DERIVS_DIR
mkdir -p $MRIQC_WORK_DIR

# Prepare binds
APPTAINER_CMD="singularity run --cleanenv -B $BIDS_DIR:/data -B $MRIQC_WORK_DIR:/work ${MRIQC_VERSION}"

# Parse the subs.txt file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed "${SLURM_ARRAY_TASK_ID}q;d" ${SUBJECTS_FILE} )

# Compose the command
cmd="${APPTAINER_CMD} /data ${MRIQC_DERIVS_DIR} participant -w /work --participant-label $subject -v --verbose-reports"

# Setup done, run the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd
exitcode=$?

# Output results to a table
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode