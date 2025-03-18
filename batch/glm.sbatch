#!/bin/bash
#
#SBATCH -J launch_glm
#SBATCH --time=04:00:00
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

# Get full path to uv executable
uv_exec=$(which uv)

# Get script paths relative to project root
# - This launches the GLM, then creates the 
# - quality assurance figures
script_files=(
    "src/network_analysis/glm/glm.py"
    "src/network_analysis/glm/create_carpet_plots.py"
    "src/network_analysis/glm/create_brain_maps.py"
)

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