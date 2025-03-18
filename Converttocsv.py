import json
import csv
import os

# Define the folder containing JSON files
json_folder_path = "./ExtractToJson"
csv_folder_path = "./CSVfiles"

# Loop through all files in the folder
for filename in os.listdir(json_folder_path):
    if filename.endswith(".json"):  # Process only JSON files
        json_path = os.path.join(json_folder_path, filename)
        csv_path = os.path.join(csv_folder_path, filename.replace(".json", ".csv"))

        # Read the JSON file
        with open(json_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Ensure data is a list of dictionaries
        if not isinstance(data, list):
            print(f"⚠️ Skipping {filename}: JSON is not a list of objects.")
            continue

        # Extract all unique keys (columns) from the JSON objects
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())

        # Write the CSV file
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(data)

        print(f"✅ Converted {filename} → {csv_path}")

print("🎉 All JSON files have been converted to CSV!")
