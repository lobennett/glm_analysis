#!/bin/bash
#
#SBATCH -J dl_get_and_unlink
#SBATCH --time=2-00:00:00
#SBATCH -n 1
#SBATCH --array 1
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



# bids=/scratch/users/logben/mnt/glm_analysis/data/validation_BIDS
# cd $bids

# echo "Loading python/3.12.1..."
# ml python/3.12.1

# # subject=$( sed "${SLURM_ARRAY_TASK_ID}q;d" ${subs}  )
# echo "Running datalad get . ..."
# ~/.local/bin/datalad get .
# echo "Running datalad unlock . ..."
# ~/.local/bin/datalad unlock .
