from neo4j import GraphDatabase
import csv
import os
import sys

# Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "itsjuleandcharlotte"

driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query, params=None):
    with driver.session() as session:
        session.run(query, parameters=params)


# 1. Similarity of Papers 
# -> Papers that are similar based on having common authors
# (:Paper)<-[:WROTE]-(:Author)-[:WROTE]->(:Paper)

# Graph Projection for Paper Similarity
query = """
CALL gds.graph.project(
    'paperSimilarityGraph',
    ['Paper', 'Author'],
    {
        WROTE: {
            orientation: 'UNDIRECTED'
        }
    }
)
"""
run_query(query)

# Run the Call 
query= """
CALL gds.nodeSimilarity.stream('paperSimilarityGraph', {
  nodeLabels: ['Paper']
})
YIELD node1, node2, similarity
WITH gds.util.asNode(node1) AS p1, gds.util.asNode(node2) AS p2, similarity
RETURN p1.title AS Paper1, p2.title AS Paper2, similarity
ORDER BY similarity DESC
LIMIT 20;
"""
run_query(query) 

# Make relations between papers from their similarity
query= """
CALL gds.nodeSimilarity.write('paperSimilarityGraph', {
  nodeLabels: ['Paper'],
  relationshipType: 'SIMILAR_TO',
  writeProperty: 'score'
})
YIELD nodesCompared, relationshipsWritten;
"""
run_query(query) 

#Drop the IN-MEMORY GRPAH eventually 
run_query("CALL gds.graph.drop('paperSimilarityGraph')")

# TO BE PROJECTED Venues with similar authors

