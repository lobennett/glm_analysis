#!/bin/bash
#
#SBATCH -J dl_save
#SBATCH --time=02:00:00
#SBATCH -n 1
#SBATCH --array 1-53
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH -p russpold,hns,normal
# Outputs ---------------------------------
#SBATCH -o ./log/%x-%A-%a.out
#SBATCH -e ./log/%x-%A-%a.err
#SBATCH --mail-user=logben@stanford.edu
#SBATCH --mail-type=END
# ------------------------------------------

# Prepare computing environment
source ./batch/setup_env.sh

echo "Moving to $BIDS_DIR"
cd $BIDS_DIR

# Loading python
ml python/3.12.1

# Parse the subs.txt file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed "${SLURM_ARRAY_TASK_ID}q;d" ${ALL_SUBJECTS_FILE} )

msg="Saving data for $subject"

# Get full path to uv executable
dl_exec=$(which datalad)

# Run the command
$dl_exec save "sub-${subject}" -m "$msg"