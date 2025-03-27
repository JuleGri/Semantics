import requests
import json
import random

# API Request Parameters
query = "Graph Database"
fields = "paperId,title,year,venue,publicationVenue,influentialCitationCount,journal,abstract,publicationTypes,citationCount,authors,references,citations"
limit = 25

# API Request URL
url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields={fields}&limit={limit}"

response = requests.get(url)

if response.status_code == 200:
    papers = response.json()["data"]
    venues = {}  # Dictionary to store unique venues
    authors = {}  # Dictionary to store unique authors
    citations = []  # List to store citations
    references = []  # List to store references
    processed_papers = []  # Store processed paper data

    for paper in papers:
        paper_id = paper.get("paperId", "N/A")
        title = paper.get("title", "N/A")
        year = paper.get("year", "Unknown")
        abstract = paper.get("abstract", "N/A")
        
        authors_list = paper.get("authors", [])  # Get authors list, or empty list if missing
        # Extract the first author's ID 
        if authors_list and isinstance(authors_list, list):  
            first_author = authors_list[0].get("authorId", "N/A")  # Get first author's ID
            other_authors = [author.get("authorId", "N/A") for author in authors_list[1:]]  # Get all other author IDs
        else:
            first_author = "N/A"
            other_authors = []  # No other authors

        citation_count = paper.get("citationCount", 0)
        influential_citation_count = paper.get("influentialCitationCount", 0)
        publication_types = paper.get("publicationTypes", [])
        venue_id = paper["publicationVenue"]["id"] if paper.get("publicationVenue") else "N/A"
        venue_name = paper["publicationVenue"]["name"] if paper.get("publicationVenue") else "N/A"
        print(venue_name)
       
       #Process the venue type, that can be none, so it needs special treatment 
        venue_data = paper.get("publicationVenue")  # Might be None
        if venue_data and isinstance(venue_data, dict):
            venue_type = venue_data.get("type", "N/A")  # Extract safely
        else:
            venue_type = "N/A"  # Default if venue_data is None
        # If venue_type is still "N/A", skip it (optional)
        if venue_type == "N/A":
            print("N/A")
        #print(f"Skipping paper {paper.get('paperId', 'Unknown')} due to missing venue type.")
            continue  # Skip this paper and move to the next one
        print(venue_type)


       # In some cases the processed paper is a journal, then well alsorun through these declarations
        if venue_type == "journal":
            #volume = paper["journal"]["volume"] if paper.get("journal") else "N/A"
            #pages = paper["journal"]["pages"] if paper.get("journal") else "N/A"
            #instead of the line above, do this, in case the journal doesnt have a volume
            journal_data = paper.get("journal")  # Might be None
            if journal_data and isinstance(journal_data, dict):
                volume = journal_data.get("volume", "N/A")  # Extract safely
                pages = journal_data.get("pages", "N/A")  # Extract safely
            else:
                volume = "N/A"
                pages = "N/A"  # Default if journal_data is None or missing keys
            journal_name = paper["journal"]["name"] if paper.get("journal") else "Unknown Journal"
        
        ######################## STORE PAPER INFO COLLECTED #######################################


        # Store paper information differently based on venue type
        if venue_type == "journal":
            processed_papers.append({
                "paperId": paper_id,
                "title": title,
                "year": year,
                "firstAuthor": first_author,
                "otherAuthors": other_authors,
                "venueId": venue_id,
                "venue": venue_name,
                "venueType": venue_type,
                "abstract" : abstract,
                "volume": volume,  # Only for journals
                "citationCount": citation_count,
                "influentialCitationCount": influential_citation_count,
                "pages": pages  # Only for journals
            })
        else:
            processed_papers.append({
                "paperId": paper_id,
                "title": title,
                "year": year,
                "firstAuthor" : first_author,
                "otherAuthors": other_authors,
                "venueId": venue_id,
                "venue": venue_name,
                "venueType": venue_type,
                "abstract" : abstract,
                "citationCount": citation_count
            })  # No 'volume' or 'pages' for non-journals

        ######################  VENUES ################################################
        
        # List of example cities
        cities = [
            "Hamburg", "Bilbao", "Barcelona", "New York", "Tokyo", "Barcelona", "Toronto", "Paris", "San Francisco",
            "London", "Amsterdam", "Vienna", "Sydney", "Copenhagen", "Rome", "Seoul"
        ]
        
        # Store unique venue with year and volume (only for journals)
        venue_key = (venue_id, venue_name, year)  # Unique identifier without volume for non-journals

        if venue_key not in venues:
            if venue_type.lower() == "journal":
                venues[venue_key] = {
                    "venueId": venue_id,
                    "venue": venue_name,
                    "year": year,
                    "type": venue_type,
                    "volume": volume  # Only for journals
                }
            else:
                random_city = random.choice(cities)  # Pick a random city
                venues[venue_key] = {
                    "venueId": venue_id,
                    "venue": venue_name,
                    "year": year,
                    "type": venue_type,
                    "city": random_city  # Add city only for conferences
                }

        # Store authors
        for author in paper.get("authors", []):
            author_id = author.get("authorId", "Unknown")
            author_name = author.get("name", "Unknown")
            hIndex = author.get("hIndex", "Unknown")
            paper_Count = author.get("paperCount", "Unknown")
            affiliations = author.get("affiliations", [])

            if author_id not in authors:
                authors[author_id] = {
                    "authorId": author_id,
                    "name": author_name,
                    "hIndex": hIndex,
                    "paper_Count" : paper_Count,
                    "affiliations": affiliations
                }

        # Store citations (papers citing this paper)
        for cited_paper in paper.get("citations", []):
            citations.append({
                "citingPaperId": paper_id,
                "citedPaperId": cited_paper.get("paperId", "Unknown")
            })

        # Store references (papers this paper references)
        for ref_paper in paper.get("references", []):
            references.append({
                "paperId": paper_id,
                "referencedPaperId": ref_paper.get("paperId", "Unknown")
            })

    # Save processed papers to JSON
    with open("papers.json", "w") as f:
        json.dump(processed_papers, f, indent=4)

    ############## MAKE CONFERENCES WITH "WORKSHOP" IN THE TITLE WORKSHOPS  #####################

    # Normalize 'workshop' venue type for conferences that contain 'workshop' in their title
    for key, venue in venues.items():
        if (
            venue["type"].lower() == "conference" and
            "workshop" in venue["venue"].lower()
        ):
            venue["type"] = "Workshop"

    # Save unique venues to JSON
    with open("venues.json", "w") as f:
        json.dump(list(venues.values()), f, indent=4)

    # Save authors to JSON
    with open("authors.json", "w") as f:
        json.dump(list(authors.values()), f, indent=4)

    # Save citations to JSON
    with open("citations.json", "w") as f:
        json.dump(citations, f, indent=4)

    # Save references to JSON
    with open("references.json", "w") as f:
        json.dump(references, f, indent=4)

    print(f"✅ Processed {len(processed_papers)} papers and saved {len(venues)} unique venues to venues.json.")
    print(f"✅ Saved {len(authors)} authors, {len(citations)} citations, and {len(references)} references.")

else:
    print(f"❌ Error fetching data: {response.status_code}, {response.text}")
