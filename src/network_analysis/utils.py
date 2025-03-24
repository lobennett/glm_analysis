import json
import argparse
from pathlib import Path

def get_path_config():
    """Get the path config from the config file."""
    with open("data/path_config.json") as f:
        data = json.load(f)

    required_keys = [
        'bids_dir', 'fmriprep_dir', 'tedana_dummy_removed_dir',
        'tedana_denoised_dir', 'tedana_transformed_dir', 'glm_data_dir'
    ]
    for key in required_keys:
        if key not in data or data[key] is None:
            raise KeyError(f"{key} is missing or None")

    return (Path(data[key]) for key in required_keys)


def get_parser():
    parser = argparse.ArgumentParser(description="Parallelize by subject ID")
    parser.add_argument("--subj-id", type=str, required=True, help="Subject ID to run")
    return parser

def get_subj_id(parser):
    assert parser is not None, "Parser is not provided"

    subj_id = parser.parse_args().subj_id

    assert subj_id is not None, "Subject ID is not provided"

    if subj_id.startswith("sub-s"):
        return subj_id
    
    if subj_id.startswith("s"):
        return f"sub-{subj_id}"
    
    return f"sub-s{subj_id}"