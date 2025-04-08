from neo4j import GraphDatabase
import csv
import os
import uuid

# Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"

driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to execute a Cypher query
def run_query(query, params=None):
    """Execute a Cypher query."""
    with driver.session() as session:
        session.run(query, parameters=params)

#Step 0: delete previous nodes and relationships
def clear_database():
    """Completely resets the database, removing all nodes, relationships, labels, and property keys."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")  # Delete nodes & relationships
        session.run("CALL apoc.schema.assert({}, {})")  # Remove constraints and indexes
        #session.run("CALL apoc.schema.node.clean(false)")  # Remove all labels & property keys
    print("Database fully cleared: all nodes, relationships, labels, and property keys deleted.")
clear_database()

# Step 1: Create uniqueness constraints
create_constraints_queries = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Author) REQUIRE a.authorId IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.paperId IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Venue) REQUIRE v.venueId IS UNIQUE;",
   # "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Review) REQUIRE r.reviewId IS UNIQUE;"
]

for query in create_constraints_queries:
    run_query(query)

# Folder containing the CSV files
folder_path = os.path.join(os.path.dirname(__file__), "../CSVfiles")

# Step 2: Import CSV files as Nodes
def import_csv_to_neo4j(csv_path, label, unique_field):
    """Import CSV data as nodes into Neo4j"""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if unique_field not in row:
                print(f"Missing {unique_field} in row: {row}")
                continue  # Skip rows with missing unique field

            # Ensure "venue" is prioritized as a display field
            if label == 'Venue':  # Only set the 'name' field for venue nodes
                row["name"] = row.get("venue", "Unknown Venue")  # Set "name" field to "venue"

            properties = ", ".join([f"{key}: ${key}" for key in row.keys()])
            query = f"MERGE (n:{label} {{ {unique_field}: ${unique_field} }}) SET n += {{ {properties} }}"
            run_query(query, row)

            #TRYING TO FIX THE PROBLEM OF NEO4J SHOWING THE VOLUME INSTEAD OF NAME FOR THE VENUES
            # Create an index on 'name' for Venue nodes (if it's a Venue node)
            if label == 'Venue':
                create_index_query = """
                           CREATE INDEX IF NOT EXISTS FOR (v:Venue) ON (v.name)
                           """
                run_query(create_index_query, {})

# Import CSV files
csv_files = {
    "authors.csv": ("Author", "authorId"),
    "papers.csv": ("Paper", "paperId"),
    "venues.csv": ("Venue", "venueId"),
}

#Import csv
for filename, (label, unique_field) in csv_files.items():
    csv_path = os.path.join(folder_path, filename)
    if os.path.exists(csv_path):
        print(f"📥 Importing {csv_path} as `{label}` nodes...")
        import_csv_to_neo4j(csv_path, label, unique_field)
        print(f"✅ `{label}` nodes imported successfully!")


# Step 3: Create Relationships
'''
# (Author)-[:WROTE]->(Paper)
with open(os.path.join(folder_path, "papers.csv"), "r", encoding="utf-8") as papers_file:
    papers_reader = csv.DictReader(papers_file)
    for paper_row in papers_reader:
        paper_id = paper_row.get("paperId")
        first_author_id = paper_row.get("firstAuthor")

        # Ensure that the firstAuthor exists in authors.csv and is used as authorId
        with open(os.path.join(folder_path, "authors.csv"), "r", encoding="utf-8") as authors_file:
            authors_reader = csv.DictReader(authors_file)
            for author_row in authors_reader:
                if author_row["authorId"] == first_author_id:
                    query = """
                    MATCH (a:Author {authorId: $authorId})
                    MATCH (p:Paper {paperId: $paperId})
                    MERGE (a)-[:WROTE]->(p)
                    """
                    params = {
                        "authorId": author_row["authorId"],
                        "paperId": paper_id
                    }
                    run_query(query, params)
                    break  # Once we find the correct author, break the inner loop

'''
'''
# (Author)-[:WROTE]->(Paper)
with open(os.path.join(folder_path, "papers.csv"), "r", encoding="utf-8") as papers_file:
    papers_reader = csv.DictReader(papers_file)
    for paper_row in papers_reader:
        paper_id = paper_row.get("paperId")
        first_author_id = paper_row.get("firstAuthor")
        other_authors_ids = paper_row.get("otherAuthors", "").split(",")  # Split by comma to handle multiple co-authors

        # Ensure the firstAuthor exists and create the relationship for first author
        with open(os.path.join(folder_path, "authors.csv"), "r", encoding="utf-8") as authors_file:
            authors_reader = csv.DictReader(authors_file)
            for author_row in authors_reader:
                if author_row["authorId"] == first_author_id:
                    query = """
                    MATCH (a:Author {authorId: $authorId})
                    MATCH (p:Paper {paperId: $paperId})
                    MERGE (a)-[:WROTE]->(p)
                    """
                    params = {
                        "authorId": author_row["authorId"],
                        "paperId": paper_id
                    }
                    run_query(query, params)
                    break  # Once we find the first author, break the loop

        # Handle co-authors (other authors) and create relationships
        for co_author_id in other_authors_ids:
            with open(os.path.join(folder_path, "authors.csv"), "r", encoding="utf-8") as authors_file:
                authors_reader = csv.DictReader(authors_file)
                for author_row in authors_reader:
                    if author_row["authorId"] == co_author_id:
                        query = """
                        MATCH (a:Author {authorId: $authorId})
                        MATCH (p:Paper {paperId: $paperId})
                        MERGE (a)-[:WROTE]->(p)
                        """
                        params = {
                            "authorId": author_row["authorId"],
                            "paperId": paper_id
                        }
                        run_query(query, params)
                        break  # Once we find the co-author, break the loop
'''

# (Author)-[:FIRST_AUTHORED]->(Paper) & (Author)-[:CO_AUTHORED]->(Paper)
with open(os.path.join(folder_path, "papers.csv"), "r", encoding="utf-8") as papers_file:
    papers_reader = csv.DictReader(papers_file)
    for paper_row in papers_reader:
        paper_id = paper_row.get("paperId")
        first_author_id = paper_row.get("firstAuthor")
        other_authors_ids = paper_row.get("otherAuthors", "").split(",") if paper_row.get("otherAuthors") else []

        # ✅ First Author Relationship
        if first_author_id and first_author_id != "N/A":
            query = """
            MATCH (a:Author {authorId: $authorId})
            MATCH (p:Paper {paperId: $paperId})
            MERGE (a)-[:FIRST_AUTHORED]->(p)
            """
            params = {"authorId": first_author_id, "paperId": paper_id}
            run_query(query, params)

        # ✅ Co-Authors Relationships
        for co_author_id in other_authors_ids:
            co_author_id = co_author_id.strip()  # Remove whitespace
            if co_author_id and co_author_id != "N/A":
                query = """
                MATCH (a:Author {authorId: $authorId})
                MATCH (p:Paper {paperId: $paperId})
                MERGE (a)-[:CO_AUTHORED]->(p)
                """
                params = {"authorId": co_author_id, "paperId": paper_id}
                run_query(query, params)


# (Paper)-[:PUBLISHED_IN]->(Venue)
with open(os.path.join(folder_path, "papers.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:

        # Check if 'paperId' and 'venueId' exist in the row
        if 'paperId' in row and 'venueId' in row:
            query = """
            MATCH (p:Paper {paperId: $paperId})
            MATCH (v:Venue {venueId: $venueId})
            MERGE (p)-[:PUBLISHED_IN]->(v)
            """
            run_query(query, row)

# (Paper)-[:CITES]->(Paper) (Citations relationship)
with open(os.path.join(folder_path, "citations.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:

        # Ensure 'citingPaperId' and 'citedPaperId' are present
        if 'citingPaperId' in row and 'citedPaperId' in row:
            query = """
            MATCH (p1:Paper {paperId: $citingPaperId})
            MATCH (p2:Paper {paperId: $citedPaperId})
            MERGE (p1)-[:CITES]->(p2)
            """
            run_query(query, row)


# (Paper)-[:REFERENCES]->(Paper) (References relationship)
with open(os.path.join(folder_path, "references.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:

        # Ensure 'paperId' and 'referencedPaperId' are present
        if 'paperId' in row and 'referencedPaperId' in row:
            query = """
            MATCH (p1:Paper {paperId: $paperId})
            MATCH (p2:Paper {paperId: $referencedPaperId})
            MERGE (p1)-[:REFERENCES]->(p2)
            """
            run_query(query, row)
'''
# (Review)-[:WROTE_REVIEW]->(Author) & (Review)-[:REVIEWS]->(Paper)
with open(os.path.join(folder_path, "reviews.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        review_id = str(uuid.uuid4())  # Generate unique review ID
        row["reviewId"] = review_id  # Add to the row dictionary

        # Create Review node
        query = """
        MERGE (r:Review {reviewId: $reviewId})
        SET r += {reviewText: $reviewText, decision: $decision}
        """
        run_query(query, row)

        # Connect Review to Author (who wrote it)
        query = """
        MATCH (a:Author {authorId: $authorId})
        MATCH (r:Review {reviewId: $reviewId})
        MERGE (a)-[:WROTE_REVIEW]->(r)
        """
        run_query(query, row)

        # Connect Review to Paper (it reviews)
        query = """
        MATCH (r:Review {reviewId: $reviewId})
        MATCH (p:Paper {paperId: $paperId})
        MERGE (r)-[:REVIEWS]->(p)
        """
        run_query(query, row)


'''
print("🎉 All CSV data and relationships successfully imported into Neo4j!")

# Close Neo4j connection
driver.close()

