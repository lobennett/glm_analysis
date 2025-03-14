#!/bin/bash
#
#SBATCH -J pull_images
#SBATCH --time=00:30:00
#SBATCH -n 1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH -p russpold,hns,normal
# Outputs ---------------------------------
#SBATCH -o ./log/%x-%A-%a.out
#SBATCH -e ./log/%x-%A-%a.err
#SBATCH --mail-user=logben@stanford.edu
#SBATCH --mail-type=END
# ------------------------------------------


: '

Name: pull_images.sbatch

Description: This script pulls the fmriprep, mriqc, and qsiprep images. 

Usage: sbatch ./batch/pull_images.sbatch

Notes: 

'

# Prepare computing environment
source ./batch/setup_env.sh

# Pull images
apptainer pull ${FMRIPREP_VERSION} docker://nipreps/fmriprep:latest
apptainer pull ${MRIQC_VERSION} docker://nipreps/mriqc:latest
apptainer pull ${QSIPREP_VERSION} docker://pennlinc/qsiprep:latest