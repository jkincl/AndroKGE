from pathlib import Path
import os
# Define the full path
full_path = Path("../data/apks/")

# Get the parent directory of the 'apks' directory
root_part = full_path.parent
os.makedirs(os.path.join(root_part, "features"), exist_ok=True)


# Use root_part for further operations, for example:
new_path = root_part / "new_folder"


print("Root part:", root_part)
print("New path:", new_path)