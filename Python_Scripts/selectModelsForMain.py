"""Based on the trajectory comparison, create the main study model list."""

import os
import shutil
import pandas as pd

from C import (
    DIR_MODELS_AMICI, DIR_MODELS_AMICI_FINAL,
    DIR_MODELS_TRAJ_AMICI)

# trajectory comparison folder
#  for BDF, abs_error = rel_error = 1e-4, abs_tolerance = rel_tolerance = 1e-12
trajectory_path = os.path.join(
    DIR_MODELS_TRAJ_AMICI,
    'comparisons_BDF_1e-12_1e-12/comparisons_1e-04_1e-04')
# Folder with all amici models
old_path = DIR_MODELS_AMICI
# Folder for only the selected amici models
new_path = DIR_MODELS_AMICI_FINAL

# Stop if the target exists already, must be removed manually
if os.path.exists(new_path) and os.listdir(new_path):
    raise ValueError(f"Target folder {new_path} exists and is not empty")

# Create the new folder
os.makedirs(new_path, exist_ok=True)

n_accept = n_reject_nosim = n_reject_nomatch = 0

for iModel in sorted(os.listdir(old_path)):
    for iFile in sorted(os.listdir(os.path.join(old_path, iModel))):
        csv_file = os.path.join(
            trajectory_path, iModel, iFile + '_whole_error.csv')
        if not os.path.exists(csv_file):
            print(f"Reject {iModel} {iFile} as trajectories could not be #"
                  "checked")
            n_reject_nosim += 1
            continue
        if not pd.read_csv(csv_file, sep='\t')['trajectories_match'][0]:
            print(f"Reject {iModel} {iFile} as trajectories do not match")
            n_reject_nomatch += 1
            continue
        shutil.copytree(
            os.path.join(old_path, iModel, iFile),
            os.path.join(new_path, iModel, iFile))
        print(f"Accept {iModel} {iFile}")
        n_accept += 1

print(f"Rejected {n_reject_nosim} models as trajectories could not be checked")
print(f"Rejected {n_reject_nomatch} models as trajectories did not match")
print(f"Accepted {n_accept} models")
