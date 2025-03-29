import os
import requests
import json
import random
import yake

# Initialize YAKE keyword extractor
kw_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=5)  # Extract up to 5 key phrases


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
    reviews = []  # List to store reviews


    for paper in papers:
        paper_id = paper.get("paperId", "N/A")
        title = paper.get("title", "N/A")
        year = paper.get("year", "Unknown")
        abstract = paper.get("abstract", "N/A")

        # Keyword Extraction with Yake
        if abstract and abstract != "N/A":
            keywords = [kw for kw, score in kw_extractor.extract_keywords(abstract)]
            print(keywords)
        else:
            keywords = []
        
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

       
       #Process the venue type, that can be none, so it needs special treatment 
        venue_data = paper.get("publicationVenue")  # Might be None
        if venue_data and isinstance(venue_data, dict):
            venue_type = venue_data.get("type", "N/A")  # Extract safely
        else:
            venue_type = "N/A"  # Default if venue_data is None
        # If venue_type is still "N/A", skip it (optional)
        if venue_type == "N/A":
        #print(f"Skipping paper {paper.get('paperId', 'Unknown')} due to missing venue type.")
            continue  # Skip this paper and move to the next one



       # In some cases the processed paper is a journal, then well also run through these declarations
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
                "keywords": keywords,
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
                "keywords": keywords,
                "citationCount": citation_count,
                "influentialCitationCount": influential_citation_count
            })  # No 'volume' or 'pages' for non-journals

        ######################  VENUES ################################################
        
        # List of example cities
        cities = [
            "Hamburg", "Bilbao", "Catania", "Barcelona", "New York", "Tokyo", "Barcelona", "Toronto", "Paris", "San Francisco",
            "London", "Amsterdam", "Vienna", "Sydney", "Copenhagen", "Rome", "Seoul", "Montreal"
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

        #################### Store authors
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

        ################### Store citations (papers citing this paper)
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

    ###################### SELECT ELIGIBLE REVIEWERS FROM ALL AUTHORS   ##########################

    all_author_ids = list(authors.keys())  # All authorIds from authors.json
    accepted_papers_count = 0  # Keep track of the number of accepted papers
    # Calculate the total number of papers
    total_papers = len(processed_papers)
    # Target acceptance rate (80%)
    target_accepted_papers = int(total_papers * 0.8)

    for paper in processed_papers:

        decisions = [review["decision"] for review in reviews if review["paperId"] == paper["paperId"]]
        # Combine first and other authors
        excluded_reviewers = set()

        first_author = paper.get("firstAuthor")
        if first_author:
            excluded_reviewers.add(first_author)

        other_authors = paper.get("otherAuthors", [])
        excluded_reviewers.update(other_authors)

        # Filter eligible reviewers
        eligible_reviewers = [a for a in all_author_ids if a not in excluded_reviewers]

        # Select a random number of reviewers (between 3 and 5)
        num_reviewers = random.randint(3, 5)
        if len(eligible_reviewers) >= num_reviewers:
            reviewers = random.sample(eligible_reviewers, num_reviewers)
        else:
            reviewers = []

        # Add reviewers to the paper
        paper["reviewers"] = reviewers

        # Create reviews and decisions

        # Helper function to generate a varied review based on keywords
        def generate_review(keywords):
            # Different review patterns
            positive_reviews = [
                f"This paper presents promising ideas about {random.choice(keywords)}.",
                f"Great insights into {random.choice(keywords)}. Could be a game changer.",
                f"Interesting research, especially the section on {random.choice(keywords)}."
            ]

            neutral_reviews = [
                f"The paper covers {random.choice(keywords)} but lacks depth in some areas.",
                f"The paper introduces {random.choice(keywords)} but needs further clarification.",
                f"Some parts of the paper on {random.choice(keywords)} are worth considering, but overall unclear."
            ]

            critical_reviews = [
                f"Not convinced by the arguments around {random.choice(keywords)}. Needs major revisions.",
                f"Significant improvements are required for the section on {random.choice(keywords)}.",
                f"Paper is lacking in depth on {random.choice(keywords)}. Needs better analysis."
            ]

            # Randomly choose a review type
            review_type = random.choice(["positive", "neutral", "critical"])

            if review_type == "positive":
                return random.choice(positive_reviews)
            elif review_type == "neutral":
                return random.choice(neutral_reviews)
            else:
                return random.choice(critical_reviews)

        # Create reviews and decisions
        for reviewer_id in reviewers:
            review_text = generate_review(keywords)  # Generate a varied review
            # Decision based on review sentiment
            if "Needs improvement" in review_text or "lacking" in review_text or "unclear" in review_text:
                decision = "no"
            elif "game changer" in review_text or "promising" in review_text:
                decision = "yes"
            else:
                decision = random.choice(["yes", "no"])  # Random decision if neutral

            reviews.append({
                "paperId": paper["paperId"],
                "authorId": reviewer_id,
                "reviewText": review_text,
                "decision": decision
            })

        # Paper acceptance logic: If 2 out of 3 reviewers say "yes", it's accepted
        decisions = [review["decision"] for review in reviews if review["paperId"] == paper["paperId"]]
        if len(reviewers) == 3:
            accepted = decisions.count("yes") >= 2  # For 3 reviewers, at least 2 "yes" are required
        elif len(reviewers) == 4:
            accepted = decisions.count("yes") >= 3  # For 4 reviewers, at least 3 "yes" are required
        elif len(reviewers) == 5:
            accepted = decisions.count("yes") >= 3  # For 5 reviewers, at least 3 "yes" are required

        # Increment the accepted paper count if accepted
        if accepted:
            accepted_papers_count += 1

        # If we've reached the target acceptance rate, stop accepting papers beyond this point
        if accepted_papers_count > target_accepted_papers:
            accepted = False  # Force acceptance to "no" if we've reached the target acceptance count

        # Update paper's accepted field
        paper["accepted"] = accepted

        # If the paper is accepted, increment the accepted_papers_count
        if accepted:
            accepted_papers_count += 1


    # After processing, print some debug information:
    print(f"Total papers processed: {total_papers}")
    print(f"Target accepted papers (80%): {target_accepted_papers}")
    print(f"Actual accepted papers: {accepted_papers_count}")

    # To verify that acceptance rate is close to 80%
    acceptance_rate = (accepted_papers_count / total_papers) * 100
    print(f"Acceptance Rate: {acceptance_rate:.2f}%")


    # Filter out only accepted papers
    accepted_papers = [paper for paper in processed_papers if paper.get("accepted")]

    # Now, remove the venues of papers that are not accepted
    accepted_venue_ids = {paper["venueId"] for paper in accepted_papers}  # Set of venue IDs linked to accepted papers

    # Remove venues linked to rejected papers
    filtered_venues = {
        key: venue for key, venue in venues.items() if venue["venueId"] in accepted_venue_ids
    }

    #Create the JSON folder PATH
    json_folder_path = "JSONfiles"
    os.makedirs(json_folder_path, exist_ok=True)

    # Save processed papers to JSON
    with open(os.path.join(json_folder_path, "papers.json"), "w") as f:
        json.dump(processed_papers, f, indent=4)
    '''
    # Save only accepted papers to JSON
    with open(os.path.join(json_folder_path, "papers.json"), "w") as f:
        json.dump(accepted_papers, f, indent=4)
    '''

    ############## MAKE CONFERENCES WITH "WORKSHOP" IN THE TITLE WORKSHOPS  #####################

    # Normalize 'workshop' venue type for conferences that contain 'workshop' in their title
    # only save venues for accepted papers
    for key, venue in filtered_venues.items():
        if (
            venue["type"].lower() == "conference" and
            "workshop" in venue["venue"].lower()
        ):
            venue["type"] = "Workshop"


    with open(os.path.join(json_folder_path, "venues.json"), "w") as f: #only save venues for accepted papers
        json.dump(list(filtered_venues.values()), f, indent=4)

    with open(os.path.join(json_folder_path, "authors.json"), "w") as f:
        json.dump(list(authors.values()), f, indent=4)

    with open(os.path.join(json_folder_path, "citations.json"), "w") as f:
        json.dump(citations, f, indent=4)

    with open(os.path.join(json_folder_path, "references.json"), "w") as f:
        json.dump(references, f, indent=4)

    with open(os.path.join(json_folder_path, "reviews.json"), "w") as f:
        json.dump(reviews, f, indent=4)

    print(f"✅ Processed {len(processed_papers)} papers and saved {len(venues)} unique venues to venues.json.")
    print(f"✅ Saved {len(authors)} authors, {len(citations)} citations, and {len(references)} references.")

else:
    print(f"❌ Error fetching data: {response.status_code}, {response.text}")
