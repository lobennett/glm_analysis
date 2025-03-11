# Network analysis 

> GLM analysis for fMRI data.

## Complete the setup

1. Initialize a git repository with `git init`
2. Run `uv sync` to install the dependencies
3. Install pre-commit (if you haven’t already)
- `pip install pre-commit`
4. Run `pre-commit install` to install the pre-commit hooks
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


## Project-specific environment variables

If you need to define environment variables for the project (e.g. API keys or simple configuration settings), 
first create the .env file (which will not be added to the git repo, in order to prevent leakage of private information):

```
cp .env.example .env
```

Then define the variables there, which can be accessed via `os.environ` in Python after using the following commands:

```
from dotenv import load_dotenv
load_dotenv()
```

Right now there are no environment variables that need to be set.

## Usage 

From the root directory, run any of the following commands:

```
# Create first level models & fixed effects for a subject
# - Results are written to ./results/
uv run glm

# Create carpet plots for quality control
# - Figures are saved to ./figures/carpet_plots/
uv run create_carpet_plots

# Create brain maps for quality control
# - Figures are saved to ./figures/brain_maps/
uv run create_brain_maps
```
