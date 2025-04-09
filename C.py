'''

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


from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"
driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query, parameters=None):
    with driver.session() as session:
        return session.run(query, parameters)

# Step 1: Define community using hybrid keyword strategy
def step1_define_database_community():
    query = """
    MERGE (rc:ResearchCommunity {name: "Database Community"})
    WITH rc
    UNWIND [
        "data management", "indexing", "data modeling", 
        "big data", "data processing", "data storage", 
        "data querying"
    ] AS kw
    MERGE (k:Keyword {name: kw})
    MERGE (rc)-[:HAS_KEYWORD]->(k)

    // Also connect RC to all other keywords that co-occur with these
    WITH rc
    MATCH (k:Keyword)<-[:CONTAINS_KEYWORD]-(:Paper)-[:CONTAINS_KEYWORD]->(related:Keyword)
    WHERE k.name IN [
        "data management", "indexing", "data modeling", 
        "big data", "data processing", "data storage", 
        "data querying"
    ]
    MERGE (rc)-[:HAS_KEYWORD]->(related)
    """
    run_query(query)

# Step 2: Identify venues where 90% of their papers contain at least one RC keyword
def step2_tag_related_venues():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})-[:HAS_KEYWORD]->(kw:Keyword)
    WITH rc, COLLECT(kw.name) AS rc_keywords

    MATCH (v:Venue)<-[:PUBLISHED_IN]-(p:Paper)
    WITH v, COLLECT(p) AS papers, rc_keywords

    UNWIND papers AS p
    OPTIONAL MATCH (p)-[:CONTAINS_KEYWORD]->(k:Keyword)
    WITH v, papers, COUNT(DISTINCT CASE WHEN k.name IN rc_keywords THEN p END) AS match_count, SIZE(papers) AS total

    WHERE total > 0 AND (1.0 * match_count / total) >= 0.9
    MATCH (rc:ResearchCommunity {name: "Database Community"})
    MERGE (v)-[:RELATED_TO]->(rc)
    """
    run_query(query)

# Step 3: Find top 100 most cited papers from those venues, cited by DB papers
def step3_identify_top_100_papers():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})-[:HAS_KEYWORD]->(kw:Keyword)
    WITH rc, COLLECT(kw.name) AS rc_keywords

    MATCH (citing:Paper)-[:CONTAINS_KEYWORD]->(k:Keyword)
    WHERE k.name IN rc_keywords
    WITH rc, citing

    MATCH (citing)-[:CITES]->(cited:Paper)-[:PUBLISHED_IN]->(v:Venue)-[:RELATED_TO]->(rc)
    WITH cited, COUNT(DISTINCT citing) AS db_citations
    ORDER BY db_citations DESC
    LIMIT 100
    MERGE (cited)-[:IS_TOP_PAPER]->(rc)
    """
    run_query(query)

# Step 4: Add reviewer and guru status based on top papers
def step4_mark_reviewers_and_gurus():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})
    MATCH (a:Author)-[:AUTHORED]->(p:Paper)-[:IS_TOP_PAPER]->(rc)
    MERGE (a)-[:POTENTIAL_REVIEWER]->(rc)

    WITH a, rc, COUNT(p) AS top_paper_count
    WHERE top_paper_count >= 2
    MERGE (a)-[:GURU]->(rc)
    """
    run_query(query)

def run_all_steps():
    print("Step 1: Defining community via mixed keyword strategy...")
    step1_define_database_community()

    print("Step 2: Identifying venues with 90% match to DB keywords...")
    step2_tag_related_venues()

    print("Step 3: Getting top-100 cited papers in related venues...")
    step3_identify_top_100_papers()

    print("Step 4: Flagging potential reviewers and gurus...")
    step4_mark_reviewers_and_gurus()

    print("✅ All steps complete. Database updated.")

run_all_steps()
driver.close()

from neo4j import GraphDatabase

# Neo4j connection parameters
uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"
driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query, parameters=None):
    with driver.session() as session:
        return session.run(query, parameters)

# Step 1: Define the Database Community with explicit keywords
def step1_define_database_community():
    query = """
    MERGE (rc:ResearchCommunity {name: "Database Community"})
    WITH rc
    UNWIND [
        "data management", "indexing", "data modeling", 
        "big data", "data processing", "data storage", 
        "data querying"
    ] AS kw
        MERGE (k:Keyword {name: kw})
        MERGE (rc)-[:HAS_KEYWORD]->(k)
    """
    run_query(query)

# Step 2: Identify venues where >=90% of papers match DB keywords
def step2_tag_related_venues():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})-[:HAS_KEYWORD]->(k:Keyword)
    WITH COLLECT(k.name) AS db_keywords

    MATCH (v:Venue)<-[:PUBLISHED_IN]-(p:Paper)
    WITH v, COLLECT(p) AS papers, db_keywords

    UNWIND papers AS p
    OPTIONAL MATCH (p)-[:CONTAINS_KEYWORD]->(kw:Keyword)
    WITH v, papers, COUNT(CASE WHEN kw.name IN db_keywords THEN 1 END) AS matching_papers, SIZE(papers) AS total_papers

    WHERE total_papers > 0 AND (1.0 * matching_papers / total_papers) >= 0.9
    MATCH (rc:ResearchCommunity {name: "Database Community"})
    MERGE (v)-[:RELATED_TO]->(rc)
    """
    run_query(query)

# Step 3: Top 100 cited papers in those venues (by DB community papers)
def step3_identify_top_100_papers():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})-[:HAS_KEYWORD]->(kw:Keyword)
    WITH rc, COLLECT(kw.name) AS db_keywords

    MATCH (citing:Paper)-[:CONTAINS_KEYWORD]->(k:Keyword)
    WHERE k.name IN db_keywords

    MATCH (citing)-[:CITES]->(p:Paper)-[:PUBLISHED_IN]->(v:Venue)-[:RELATED_TO]->(rc)
    WITH p, COUNT(citing) AS db_citations
    ORDER BY db_citations DESC
    LIMIT 100
    MERGE (p)-[:IS_TOP_PAPER]->(rc)
    """
    run_query(query)

# Step 4: Mark potential reviewers and gurus
def step4_mark_reviewers_and_gurus():
    query = """
    MATCH (rc:ResearchCommunity {name: "Database Community"})
    MATCH (a:Author)-[:AUTHORED]->(p:Paper)-[:IS_TOP_PAPER]->(rc)
    MERGE (a)-[:POTENTIAL_REVIEWER]->(rc)

    WITH rc, a, COUNT(p) AS top_paper_count
    WHERE top_paper_count >= 2
    MERGE (a)-[:GURU]->(rc)
    """
    run_query(query)

def run_all_steps():
    print("Step 1: Defining community with keywords...")
    step1_define_database_community()

    print("Step 2: Identifying database-related venues...")
    step2_tag_related_venues()

    print("Step 3: Finding top-100 papers by citations from DB papers...")
    step3_identify_top_100_papers()

    print("Step 4: Marking potential reviewers and gurus...")
    step4_mark_reviewers_and_gurus()

    print("✅ Done! Graph updated with 4 precise queries.")

run_all_steps()
driver.close()
'''

from neo4j import GraphDatabase

# Neo4j connection parameters
uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"
driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query, parameters=None):
    with driver.session() as session:
        return session.run(query, parameters)

# Step 1: Define Research Communities and Keywords
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




# 2. Identify related venues where >=90% of papers contain RC keywords
def identify_related_venues():
    query = """
    MATCH (rc:ResearchCommunity)-[:HAS_KEYWORD]->(kw:Keyword)
    MATCH (v:Venue)<-[:PUBLISHED_IN]-(p:Paper)-[:CONTAINS_KEYWORD]->(kw)
    WITH v, COUNT(DISTINCT p) AS totalPapers, COUNT(DISTINCT kw) AS relevantKeywords
    WHERE relevantKeywords / totalPapers >= 0.9
    MERGE (v)-[:RELATED_TO]->(rc)
    """
    run_query(query)

# 3. Identify the Top 100 Papers by Citation Count
def identify_top_papers():
    query = """
    MATCH (rc:ResearchCommunity)-[:HAS_KEYWORD]->(kw:Keyword)
    MATCH (p:Paper)-[:CONTAINS_KEYWORD]->(kw)
    MATCH (p)<-[:CITES]-(citedPaper:Paper)
    WITH p, COUNT(citedPaper) AS citationCount
    ORDER BY citationCount DESC
    LIMIT 100
    MERGE (p)-[:IS_TOP_PAPER]->(rc)
    """
    run_query(query)

# Step 4: Mark potential reviewers and gurus based on top papers
def identify_reviewers_and_gurus():
    # Identify Potential Reviewers
    query_reviewers = """
    MATCH (rc:ResearchCommunity)-[:HAS_KEYWORD]->(kw:Keyword)
    MATCH (p:Paper)-[:CONTAINS_KEYWORD]->(kw)
    MATCH (a:Author)-[:AUTHORED]->(p)-[:IS_TOP_PAPER]->(rc)
    MERGE (a)-[:POTENTIAL_REVIEWER]->(rc)
    """
    run_query(query_reviewers)

    # Identify Gurus (Authors with at least two top papers)
    query_gurus = """
    MATCH (rc:ResearchCommunity)-[:HAS_KEYWORD]->(kw:Keyword)
    MATCH (p:Paper)-[:CONTAINS_KEYWORD]->(kw)
    MATCH (a:Author)-[:AUTHORED]->(p)-[:IS_TOP_PAPER]->(rc)
    WITH a, COUNT(p) AS topPapers
    WHERE topPapers >= 2
    MERGE (a)-[:GURU]->(rc)
    """
    run_query(query_gurus)

# Run all the steps sequentially
def run_all_steps():
    print("Step 1: Defining the research communities and linking keywords...")
    define_research_communities()
    print("Step 1 completed.")

    print("Step 2: Identifying related venues (optional)...")
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

