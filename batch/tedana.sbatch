#!/bin/bash
#
#SBATCH -J tedana
#SBATCH --time=2-00:00:00
#SBATCH -n 1
#SBATCH --array 1 # TODO: Change this to the number of subjects
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

Name: tedana.sbatch

Description: This script runs tedana on a dataset. 

Usage: sbatch ./batch/tedana.sbatch

Notes: 

'

# Get script paths relative to project root
script_files=(
    "src/network_analysis/tedana/01_remove_dummy_trs.py"
    "src/network_analysis/tedana/02_denoise_data.py"
    "src/network_analysis/tedana/03_tedana_transform.py"
    "src/network_analysis/tedana/04_prepare_glm_directory.py"
)

# Get full path to uv executable
uv_exec=$(which uv)

# Run each script using the uv executable
for script in "${script_files[@]}"; do
    echo "Running script: $script"
    $uv_exec run "$script"
    echo "Completed script: $script"
done

echo "All scripts completed"

exitcode=$?
echo "Exit code: $exitcode"
exit $exitcode
