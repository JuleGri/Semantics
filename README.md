# Semantics
Research Paper Graph Database

1. Run requirements.txt and download Neo4J Desktop.
2. Run Extract_to_json.py to connect to the API and extract the data in json files. (A.2)
3. Run Converttocsv.py to convert these json files to csv. (A.2)
4. Start the database from Neo4j Desktop and run neo4j_connection.py to establish the connection with Neo4j desktop and import the csv to the graph database. (A.2)
    Starting the database from Neo4j Desktop: 

5. A.3. Evolving the graph: run A3.py and restart DB in Neo4j Desktop. Inside this script, it does:
   1. Run evolving_graph.py to create the new json files needed to evolve the graph (adding reviews and filtering out papers and venues). 
   2. Re-run Converttocsv.py to convert the resulting json files into csv.
   3. Run new_neo4_connection.py to convert run the Cypher queries needed to evolve the graph.
   
6. Run querying.py to run the Cypher queries for part B.
7. Run recommender.py to run the Cypher queries for part C.
8. Run graph_alg.py to run the Cypher queries for part D.
9. 