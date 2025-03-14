#!/bin/bash

# Base paths 
export BIDS_DIR="./data/fMRI_data"
export APPTAINER_DIR="./apptainer_images"

# fMRIPrep version
# - NOTE: Change tags to match the version you want to use
export TAG="latest" 
export TIMESTAMP="20250313"
export FMRIPREP_VERSION="${APPTAINER_DIR}/fmriprep_${TAG}_${TIMESTAMP}.sif"

# MRIQC version
export MRIQC_VERSION="latest"
export MRIQC_VERSION="${APPTAINER_DIR}/mriqc_${MRIQC_VERSION}_${TIMESTAMP}.sif"

# QSIPrep version
export QSIPREP_VERSION="latest"
export QSIPREP_VERSION="${APPTAINER_DIR}/qsiprep_${QSIPREP_VERSION}_${TIMESTAMP}.sif"

# - FMRIPrep
export FMRIPREP_DERIVS_DIR="${BIDS_DIR}/derivatives/fmriprep-${TAG}"
export FMRIPREP_WORK_DIR="./work/fmriprep_${TAG}"
# - MRIQC
export MRIQC_DERIVS_DIR="${BIDS_DIR}/derivatives/mriqc-${TAG}"
export MRIQC_WORK_DIR="./work/mriqc_${TAG}"
# - QSIPrep
export QSIPREP_DERIVS_DIR="${BIDS_DIR}/derivatives/qsiprep-${TAG}"
export QSIPREP_WORK_DIR="./work/qsiprep_${TAG}"

# Batch input
## Only running on completed subjects
export SUBJECTS_FILE="./subs.txt"

# FreeSurfer license
# - NOTE: Change this to the path to your FreeSurfer license file
export FS_LICENSE="$HOME/license.txt"