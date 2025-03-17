# Network analysis 

> Preprocessing and GLM pipeline for network fMRI data.

## Complete the setup

1. First, clone the GitHub repository. 
- `git clone -b example https://github.com/lobennett/glm_analysis.git`
2. Run `uv sync` to install the dependencies
3. (Optional) Install and setup pre-commit
- Install with  `pip install pre-commit`
- Run `pre-commit install` to install the pre-commit hooks
	- pre-commit installed at `.git/hooks/pre-commit`
5. (Optional) Set up VS Code so that it lints/formats on save
- Create `.vscode/settings.json` to configure your workspace settings: `mkdir .vscode && touch .vscode/settings.json`
- Paste the following settings into `.vscode/settings.json`:
```json
{
    "notebook.formatOnSave.enabled": true,
    "notebook.formatOnCellExecution": true,
    "notebook.defaultFormatter": "charliermarsh.ruff",
    "notebook.codeActionsOnSave": {
        "notebook.source.fixAll": "explicit",
        "notebook.source.organizeImports": "explicit",
    },
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit",
        }
    },
}
```

## Usage 

> [!NOTE]
> ### On Data and SLURM
> This repository assumes you have access to the BIDS data directory. Currently, the directory lives on russpold's $OAK partition. You will not need access to the derivatives. So if you would like, you can symbolic link the BIDS data, then run the whole the whole pipeline from scratch. (I haven't tested this, so there are likely things that I'd need to adjust before this works smoothly. The hope is that given our BIDS data one would be able to run everything up to and including second-level maps.) 
> 
> Also, the pipeline is currently only fit to run on a single subject's data (`s1273`). I wanted to test how feasible it would be to refactor the pipeline, and so some of the scripts here would need to be adjusted before being able to be applied to the full dataset. For example, instead of hardcoding the subject ID in the script, it could be read in as a flag or through lines in [subs.txt](./subs.txt), and then execution of the pipeline could be parallelized by the batch `--array` flag. 
> 
> It is also (probably) unnecessary to re-run MRIQC and fMRIPrep on the BIDS data. I included those batch scripts as examples of how we could organize things for new projects that have not yet had their MRIQC and fMRIPrep derivatives quality assured. We also used different versions that those that would be pulled from [./batch/pull_images.sbatch](./batch/pull_images.sbatch). If we want to make this more reproducible, we should pull the image versions we actually used instead of the latest ones. 

First, pull all apptainer images to `./apptainer_images/`. This will give you the latest versions of fMRIPrep, MRIQC, and QSIPrep.

```
# Pull apptainer images 
sbatch ./batch/pull_images.sbatch
```

You can run the apptainer images with the following commands. 
```
# fMRIPrep
sbatch ./batch/fmriprep.sbatch
# MRIQC
sbatch ./batch/mriqc.sbatch
# QSIPrep
sbatch ./batch/qsiprep.sbatch
```

Once fMRIPrep has completed, you can run tedana on its outputs. This will remove the `non_steady_state_outlier` TRs, create a denoised image based on the multi-echo scans, and align these images to T1w or MNI space. The tedana batch script just executes the scripts in the [tedana module](./src/network_analysis/tedana/) one at a time.

```
# Launch the tedana pipeline
sbatch ./batch/tedana.sbatch
```
> [!NOTE]
> `./batch/tedana.sbatch` might time out. It has a time limit of two days. If it does fail to complete in the alloted time, you can just re-run it, and it'll skip over the outputs that already exist. 

Once the tedana job completes successfully, you will have a directory containing all the data needed for first-level models. This directory will be created at `./data/glm_data`. 

To run the first-level models, run the following commands.
```
# Run single subject fixed effects models
# - Output written to ./results/
uv run glm

# Create carpet plots for quality control
# - Figures saved to ./figures/carpet_plots/
uv run create_carpet_plots

# Create brain maps for quality control
# - Figures saved to ./figures/brain_maps/
uv run create_brain_maps
```

## Things to add

- [ ] 1. Module to fetch data from Flywheel and convert it to BIDS
- [ ] 2. Module for converting raw behavioral data to events files. 
- [ ] 3. Module for second-level maps
- [ ] 4. Parallelize scripts by subject IDs (and session IDs?)
- [ ] 5. Test full pipeline to ensure batch jobs work as expected
- [ ] 6. Extract out core, shared functions to their own python package (e.g., function to calculate VIFs given contrasts)