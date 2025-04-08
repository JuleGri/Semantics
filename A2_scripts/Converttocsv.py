import json
import csv
import os

# Define the folder containing JSON files
json_folder_path = os.path.join(os.path.dirname(__file__), "../JSONfiles")
csv_folder_path = os.path.join(os.path.dirname(__file__), "../CSVfiles")

print(f"JSON folder path: {json_folder_path}")
print(f"CSV folder path: {csv_folder_path}")

def flatten_dict(d, parent_key='', sep='_'):
    """Recursively flattens nested dictionaries."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ", ".join(map(str, v))))  # Convert lists to CSV-friendly strings
        else:
            items.append((new_key, v))
    return dict(items)


# Ensure CSV folder exists
os.makedirs(csv_folder_path, exist_ok=True)

# 🗑️ DELETE old CSV files to prevent duplicates
for old_file in os.listdir(csv_folder_path):
    if old_file.endswith(".csv"):
        os.remove(os.path.join(csv_folder_path, old_file))
print("🗑️ Old CSV files deleted. Creating new ones...")

# Loop through JSON files
for filename in os.listdir(json_folder_path):
    if filename.endswith(".json"):  # Only process JSON files
        json_path = os.path.join(json_folder_path, filename)
        csv_path = os.path.join(csv_folder_path, filename.replace(".json", ".csv"))

        # Read JSON file
        with open(json_path, "r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                print(f"❌ Skipping {filename}: Invalid JSON format.")
                continue

        # Ensure data is a list of dictionaries
        if not isinstance(data, list):
            print(f"⚠️ Skipping {filename}: JSON root element is not a list.")
            continue

        # Flatten all JSON objects
        flattened_data = [flatten_dict(item) for item in data]

        # Extract all unique keys (columns)
        all_keys = set()
        for item in flattened_data:
            all_keys.update(item.keys())

        # Write CSV file
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(flattened_data)

        print(f"✅ Converted {filename} → {csv_path}")

print("🎉 All JSON files have been successfully converted to CSV!")