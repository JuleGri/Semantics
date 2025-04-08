from neo4j import GraphDatabase

# Neo4j connection parameters
uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to run a Cypher query
def run_query(query, parameters=None):
    with driver.session() as session:
        return session.run(query, parameters)

# 1. Define the Research Communities with Keywords
def define_research_communities():
    communities = {
        'Database Community': ['data management', 'indexing', 'data modeling', 'big data', 'data processing', 'data storage', 'data querying'],
        'Machine Learning Community': ['machine learning', 'deep learning', 'supervised learning', 'unsupervised learning'],
        'Artificial Intelligence Community': ['artificial intelligence', 'neural networks', 'AI algorithms', 'computer vision'],
        'Natural Language Processing (NLP) Community': ['natural language processing', 'text mining', 'sentiment analysis', 'speech recognition'],
        'Computer Vision Community': ['computer vision', 'image processing', 'object detection', 'facial recognition', 'image segmentation', 'deep learning', 'convolutional neural networks (CNNs)']
    }

    for community_name, keywords in communities.items():
        # Step 1: Create the ResearchCommunity node
        query = """
        MERGE (rc:ResearchCommunity {name: $communityName})
        """
        run_query(query, {"communityName": community_name})

        # Step 2: Create Keyword nodes and relationships to the community
        for keyword in keywords:
            query = """
            MERGE (k:Keyword {name: $keyword})
            MERGE (rc)-[:HAS_KEYWORD]->(k)
            """
            run_query(query, {"communityName": community_name, "keyword": keyword})

        # Step 3: Link Papers related to the ResearchCommunity based on Keywords
        query = """
        MATCH (p:Paper)-[:CONTAINS_KEYWORD]->(k:Keyword)
        MATCH (rc:ResearchCommunity {name: $communityName})
        WHERE k.name IN $keywords
        MERGE (p)-[:BELONGS_TO]->(rc)  // Link papers to the community
        """
        run_query(query, {"communityName": community_name, "keywords": keywords})

        # Step 4: Link Venues where papers are published to the community
        query = """
        MATCH (p:Paper)-[:PUBLISHED_IN]->(v:Venue)
        MATCH (rc:ResearchCommunity {name: $communityName})
        WHERE (p)-[:BELONGS_TO]->(rc)  // Make sure the papers are already linked to the community
        MERGE (v)-[:HOSTS]->(rc)
        """
        run_query(query, {"communityName": community_name})

# 2. Identify Conferences, Workshops, and Journals Related to Research Communities
def identify_related_venues():
    query = """
    MATCH (v:Venue)-[:HOSTS]->(p:Paper)-[:CONTAINS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(rc:ResearchCommunity)
    WITH v, COUNT(DISTINCT p) AS totalPapers, COUNT(DISTINCT k) AS relevantPapers
    WHERE relevantPapers / totalPapers >= 0.9
    MERGE (v)-[:RELATED_TO]->(rc)
    """
    run_query(query)

# 3. Identify the Top 100 Papers by Citation Count
def identify_top_papers():
    query = """
    MATCH (p:Paper)-[:PUBLISHED_IN]->(v:Venue)-[:RELATED_TO]->(rc:ResearchCommunity)
    MATCH (p)<-[:CITES]-(citedPaper:Paper)
    WITH p, COUNT(citedPaper) AS citationCount
    ORDER BY citationCount DESC
    LIMIT 100
    MERGE (p)-[:IS_TOP_PAPER]->(rc)
    """
    run_query(query)

# 4. Identify Potential Reviewers and Gurus
def identify_reviewers_and_gurus():
    # Identify Potential Reviewers
    query_reviewers = """
    MATCH (p:Paper)-[:IS_TOP_PAPER]->(rc:ResearchCommunity)<-[:AUTHORED]-(a:Author)
    MERGE (a)-[:POTENTIAL_REVIEWER]->(rc)
    """
    run_query(query_reviewers)

    # Identify Gurus (Authors with at least two top papers)
    query_gurus = """
    MATCH (p:Paper)-[:IS_TOP_PAPER]->(rc:ResearchCommunity)<-[:AUTHORED]-(a:Author)
    WITH a, COUNT(p) AS topPapers
    WHERE topPapers >= 2
    MERGE (a)-[:GURU]->(rc)
    """
    run_query(query_gurus)

# Execute the steps in order
def run_all_steps():
    print("Step 1: Defining the research communities...")
    define_research_communities()
    print("Step 1 completed.")

    print("Step 2: Identifying related venues...")
    identify_related_venues()
    print("Step 2 completed.")

    print("Step 3: Identifying top 100 papers...")
    identify_top_papers()
    print("Step 3 completed.")

    print("Step 4: Identifying potential reviewers and gurus...")
    identify_reviewers_and_gurus()
    print("Step 4 completed.")

# Run the full process
run_all_steps()

# Close the Neo4j connection
driver.close()

print("Recommender graph extension complete.")
