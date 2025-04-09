# Semantics
Research Paper Graph Database

1. Run requirements.txt and download Neo4J Desktop.

2. A.2. Instantiating and Loading into the graph: start DB in Neo4j Desktop and run A2.py. Inside this script, it does:
   1. Run Extract_to_json.py to connect to the API and extract the data in json files. 
   2. Run Converttocsv.py to convert these json files to csv. 
   3. Run neo4j_connection.py to establish the connection with Neo4j desktop and import the csv to the graph database. (A.2)

3. A.3. Evolving the graph: restart DB in Neo4j Desktop and run A3.py.  Inside this script, it does:
   1. Run evolving_graph.py to create the new json files needed to evolve the graph (adding reviews and filtering out papers and venues). 
   2. Re-run Converttocsv.py to convert the resulting json files into csv.
   3. Run new_neo4_connection.py to convert run the Cypher queries needed to evolve the graph.
   
4. B. Querying: run B.py, to run the Cypher queries for part B.
  
7. Run recommender.py to run the Cypher queries for part C.
8. Run graph_alg.py to run the Cypher queries for part D.
9. 