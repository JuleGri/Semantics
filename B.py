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

# 1. 3 most cited papers per venue
query= """
MATCH (p:Paper)-[:PUBLISHED\_IN]->(v:Venue)\\
    WHERE v.type IN ["conference", "workshop"]\\

    WITH v.venue AS venueName, v.year AS year, p
    ORDER BY p.citationCount DESC
    WITH venueName, year, COLLECT({title: p.title, citationCount: p.citationCount})[0..3] AS topPapers
    """
run_query(query)


# 2. Per venue (in general, not one specific edition), find the author community with authors that have published in 4 different editions of that venue
query= """
MATCH (a:Author)-[:FIRST_AUTHORED|CO_AUTHORED]->(p:Paper)-[:PUBLISHED_IN]->(v:Venue)
WHERE v.type IN ["conference", "workshop"]
WITH a.name AS authorName, v.venue AS venueName, COLLECT(DISTINCT v.year) AS years
WHERE SIZE(years) >= 4
RETURN venueName, authorName, SIZE(years) AS editionsPublishedIn
ORDER BY venueName, editionsPublishedIn DESC;

"""
run_query(query)

# 3. Find Impact Factor per Journal
#Cypher Query for 2023:
query = """
WITH [2021, 2022] AS citedYears, 2023 AS citingYear

MATCH (citing:Paper)-[:CITES]->(cited:Paper)-[:PUBLISHED_IN]->(v:Venue)
WHERE v.type = "journal" 
  AND cited.year IN citedYears 
  AND citing.year = citingYear

WITH v.venue AS journalName, COUNT(citing) AS totalCitations

MATCH (v:Venue)<-[:PUBLISHED_IN]-(p:Paper)
WHERE v.type = "journal" AND p.year IN citedYears
WITH journalName, totalCitations, COUNT(p) AS paperCount
WHERE paperCount > 0
RETURN journalName, 
       totalCitations * 1.0 / paperCount AS impactFactor,
       totalCitations, paperCount
ORDER BY impactFactor DESC;
    """
run_query(query)

# 4. Find hIndex per Author
query = """
MATCH (a:Author)-[:FIRST_AUTHORED|CO_AUTHORED]->(p:Paper)
    WITH a.name AS authorName, collect(p.citationCount) AS citations

    WITH authorName, apoc.coll.sort(citations) AS sortedCitations
    WITH authorName, 
        [i IN range(0, size(sortedCitations)-1) 
        WHERE sortedCitations[-i-1] >= i+1 | i+1] AS hCandidates

    WITH authorName, hCandidates, 
        CASE 
            WHEN size(hCandidates) = 0 THEN 0 
            ELSE max(hCandidates) 
        END AS hIndex

    RETURN authorName, hIndex
    ORDER BY hIndex DESC;
"""
run_query(query)