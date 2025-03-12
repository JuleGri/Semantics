from neo4j import GraphDatabase
import requests

# Connect to Neo4j
NEO4J_URI = "neo4j://localhost:7687"  # Use your actual DBMS URL
USERNAME = "neo4j"  # Change if needed
PASSWORD = "julecharlotte"

query = "learning | machine"
fields = "paperId,title,year,abstract,venue,citationCount,authors"

driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))
url = f"http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year=2024-"


# Function to insert data
def insert_paper(tx, paper_id, title, year, venue, citation_count):
    query = """
    MERGE (p:Paper {paperId: $paper_id})
    SET p.title = $title, p.year = $year, p.venue = $venue, p.citationCount = $citation_count
    """
    tx.run(query, paper_id=paper_id, title=title, year=year, venue=venue, citation_count=citation_count)

# Load data into Neo4j
def load_data_into_neo4j(papers):
    with driver.session() as session:
        for paper in papers:
            session.write_transaction(
                insert_paper, 
                paper.get("paperId"), 
                paper.get("title", "Unknown"), 
                paper.get("year", 0), 
                paper.get("venue", "Unknown"), 
                paper.get("citationCount", 0)
            )
    print("Data successfully inserted into Neo4j!")

url = f"http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year=2024-"


# Fetch papers
response = requests.get(url)
if response.status_code == 200:
    papers = response.json()["data"]
    load_data_into_neo4j(papers)
else:
    print(f"Error fetching data: {response.status_code}, {response.text}")

# Close connection
driver.close()
