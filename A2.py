import subprocess
import sys
import os

print("Python executable being used: ", sys.executable)

print(f"Current working directory: {os.getcwd()}")

# Define the paths to the scripts
extract_json_script = "A2_scripts/extract_to_json.py"
converttocsv_script = "A2_scripts/Converttocsv.py"
neo4_connection_script = "A2_scripts/neo4j_connection.py"
python_executable = "/Library/Developer/CommandLineTools/usr/bin/python3"

# Run evolving_graph.py to create the new json files
print("Running extract_to_json.py...")
subprocess.run([python_executable, extract_json_script], check=True)

# Run Converttocsv.py to convert the resulting json files into csv
print("Running Converttocsv.py...")
subprocess.run([python_executable, converttocsv_script], check=True)

# Run new_neo4_connection.py to run the Cypher queries and evolve the graph
print("Running neo4_connection.py...")
subprocess.run([python_executable, neo4_connection_script], check=True)

print(" Graph instantiating and Loading process completed successfully!")
