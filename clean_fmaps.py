import os
import json
import subprocess

bids = "./data/validation_BIDS"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

for sub in os.listdir(bids):
    if sub.startswith("sub-"):
        for ses in os.listdir(os.path.join(bids, sub)):
            fmap_dir = os.path.join(bids, sub, ses, "fmap")
            if os.path.exists(fmap_dir):
                for fmap in os.listdir(fmap_dir):
                    if not fmap.endswith(".json"):
                        continue
                    fullpath = os.path.join(fmap_dir, fmap)
                    
                    # Unlock the file first using datalad
                    try:
                        subprocess.run(["datalad", "unlock", fullpath], check=True)
                        print(f"Unlocked {fullpath}")
                    except subprocess.CalledProcessError:
                        print(f"Warning: Could not unlock {fullpath}, may not be able to modify")
                    
                    # Now try to modify the file
                    try:
                        data = load_json(fullpath)
                        # Remove the "IntendedFor" field
                        data.pop("IntendedFor", None)
                        data.pop('Units', None)
                        # Save the cleaned JSON
                        with open(fullpath, "w") as f:
                            json.dump(data, f, indent=4)
                        print(f"Cleaned {fullpath}")
                    except Exception as e:
                        print(f"Error processing {fullpath}: {e}")

# After all modifications, save changes to the dataset
print("Saving changes to DataLad dataset...")
subprocess.run(["datalad", "save", "-m", "Remove IntendedFor and Units fields from fieldmap JSONs"])
