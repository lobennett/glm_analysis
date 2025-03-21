#!/bin/bash
#
#SBATCH -J dl_merge
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


# s=/scratch/users/logben/validation_BIDS
# cd $s
# ml python/3.12.1
# ~/.local/bin/datalad update --merge
