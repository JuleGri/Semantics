import json
import random
import yake

with open('JSONfiles/papers.json') as f:
    papers = json.load(f)
with open('JSONfiles/authors.json') as f:
    authors = json.load(f)
with open('JSONfiles/venues.json') as f:
    venues = json.load(f)

# Initialize YAKE keyword extractor
kw_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=5)  # Extract up to 5 key phrases
all_author_ids = list(authors.keys())  # All authorIds from authors.json
accepted_papers_count = 0  # Keep track of the number of accepted papers
# Calculate the total number of papers
processed_papers = []
total_papers = len(processed_papers)
# Target acceptance rate (80%)
target_accepted_papers = int(total_papers * 0.8)
# Create reviews and decisions
# Create reviews and decisions

for paper in papers:
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
                f"Not convinced by the arguments around {random.choice(keywords)}. "
                f"Needs major revisions.",                f"Significant improvements are required for the section on {random.choice(keywords)}.",
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
    for reviewer_id in authors.reviewers:
        review_text = generate_review(authors.keywords)  # Generate a varied review
                # Decision based on review sentiment
        if "Needs improvement" in review_text or "lacking" in review_text or "unclear" in review_text:                decision = "no"
        elif "game changer" in review_text or "promising" in review_text:
           decision = "yes"
        else:
            decision = random.choice(["yes", "no"])  # Random decision if neutral
            authors.reviews.append({
            "paperId": paper["paperId"],
            "authorId": reviewer_id,
            "reviewText": review_text,
            "decision": decision
                })

            # Paper acceptance logic: If 2 out of 3 reviewers say "yes", it's accepted
    decisions = [review["decision"] for review in authors.reviews if review["paperId"] == paper["paperId"]]
    if len(authors.reviewers) == 3:
        accepted = decisions.count("yes") >= 2  # For 3 reviewers, at least 2 "yes" are required
    elif len(authors.reviewers) == 4:
        accepted = decisions.count("yes") >= 3  # For 4 reviewers, at least 3 "yes" are required
    elif len(authors.reviewers) == 5:
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