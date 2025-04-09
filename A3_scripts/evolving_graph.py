import json
import random
import os

# Helper function to generate a varied review based on keywords
def generate_review(keywords):
    # If no keywords are available, use a default keyword to avoid empty list issues
    if not keywords:
        keywords = ["general research topic"]  # Default placeholder if no keywords are provided

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


'''
# Load papers with possible reviewers
with open("../JSONfiles/papers.json", "r") as f:
    processed_papers = json.load(f)

# Load venues data (list format)
with open("../JSONfiles/venues.json", "r") as f:
    venues = json.load(f)
'''

# Define the folder path dynamically based on the script location
base_folder = os.path.dirname(os.path.abspath(__file__))

# Get the file paths using os.path.join for cross-platform compatibility
papers_file_path = os.path.join(base_folder, "..", "JSONfiles", "papers.json")
venues_file_path = os.path.join(base_folder, "..", "JSONfiles", "venues.json")
reviews_file_path = os.path.join(base_folder, "..", "JSONfiles", "reviews.json")
papers_with_acceptance_file_path = os.path.join(base_folder, "..", "JSONfiles", "papers_with_acceptance.json")
accepted_venues_file_path = os.path.join(base_folder, "..", "JSONfiles", "accepted_venues.json")

# Load papers with possible reviewers
with open(papers_file_path, "r") as f:
    processed_papers = json.load(f)

# Load venues data (list format)
with open(venues_file_path, "r") as f:
    venues = json.load(f)

# Initialize a list for reviews
reviews = []

# Initialize a counter for accepted papers
accepted_papers_count = 0

# Prepare the set of accepted venue IDs for filtering
accepted_venue_ids = set()

# Iterate over all papers and generate reviews
for paper in processed_papers:

    reviewers = paper["reviewers"]

    # If there are enough eligible reviewers, select 3-5 random ones
    num_reviewers = random.randint(3, 5)
    if len(reviewers) >= num_reviewers:
        selected_reviewers = random.sample(reviewers, num_reviewers)
    else:
        selected_reviewers = reviewers  # If not enough reviewers, take all

    # Add reviewers to paper data
    paper["reviewers"] = selected_reviewers

    # Get keywords for review generation
    keywords = paper.get("keywords", [])

    # Generate reviews for selected reviewers
    for reviewer_id in selected_reviewers:
        review_text = generate_review(keywords)  # Generate a varied review

        # Decision logic based on review sentiment
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
    accepted = decisions.count("yes") >= 2  # For 3 reviewers, at least 2 "yes" are required
    paper["accepted"] = accepted

    # Increment the accepted paper count if accepted
    if accepted:
        accepted_papers_count += 1
        accepted_venue_ids.add(paper["venueId"])  # Add accepted venue's ID

# Filter accepted venues based on accepted venue IDs
accepted_venues = [venue for venue in venues if venue["venueId"] in accepted_venue_ids]

# Save reviews to JSON
with open(reviews_file_path, "w") as f:
    json.dump(reviews, f, indent=4)

# After processing, print some debug information:
print(f"Total papers processed: {len(processed_papers)}")
print(f"Total accepted papers: {accepted_papers_count}")

# Save updated papers with acceptance status
with open(papers_with_acceptance_file_path, "w") as f:
    json.dump(processed_papers, f, indent=4)

# Save accepted venues to JSON
with open(accepted_venues_file_path, "w") as f:
    json.dump(accepted_venues, f, indent=4)

