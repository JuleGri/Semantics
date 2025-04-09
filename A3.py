import subprocess
import sys
print("Python executable being used: ", sys.executable)


# Define the paths to the scripts
evolving_graph_script = "A3_scripts/evolving_graph.py"
converttocsv_script = "A2_scripts/Converttocsv.py"
new_neo4_connection_script = "A3_scripts/new_neo4j_connection.py"
python_executable = "/Library/Developer/CommandLineTools/usr/bin/python3"

# Run evolving_graph.py to create the new json files
print("Running evolving_graph.py...")
subprocess.run([python_executable, evolving_graph_script], check=True)

# Run Converttocsv.py to convert the resulting json files into csv
print("Running Converttocsv.py...")
subprocess.run([python_executable, converttocsv_script], check=True)

# Run new_neo4_connection.py to run the Cypher queries and evolve the graph
print("Running new_neo4_connection.py...")
subprocess.run([python_executable, new_neo4_connection_script], check=True)

print(" Graph evolution process completed successfully!")
