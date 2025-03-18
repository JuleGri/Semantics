from neo4j import GraphDatabase
import csv
import os

# Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "yourpassword"  # Change this

driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to execute a Cypher query
def run_query(query, params=None):
    """Execute a Cypher query."""
    with driver.session() as session:
        session.run(query, parameters=params)

# Step 1: Create uniqueness constraints (adjust based on your CSV files)
create_constraints_queries = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Author) REQUIRE a.authorId IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.paperId IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (j:Journal) REQUIRE j.name IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.name IS UNIQUE;"
]

for query in create_constraints_queries:
    run_query(query)

# Folder containing the CSV files
folder_path = "./data"  # Update with your actual folder

# Step 2: Import CSV files as Nodes
def import_csv_to_neo4j(csv_path, label):
    """Import CSV data as nodes into Neo4j"""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            properties = ", ".join([f"{key}: ${key}" for key in row.keys()])
            query = f"MERGE (n:{label} {{ {properties} }})"
            run_query(query, row)

# Process all CSV files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        csv_path = os.path.join(folder_path, filename)
        label = filename.replace(".csv", "")  # Use filename as Neo4j label

        print(f"📥 Importing {csv_path} as `{label}` nodes...")
        import_csv_to_neo4j(csv_path, label)
        print(f"✅ `{label}` nodes imported successfully!")

print("🎉 All CSV data successfully imported into Neo4j!")

# Close Neo4j connection
driver.close()

