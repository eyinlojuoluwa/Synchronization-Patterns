import pandas as pd
import re
from huggingface_hub import ModelCard

def extract_links_from_card(model_card, model_name):
    github_links = set()  # Use a set to store unique GitHub links

    if model_card and model_card.content:
        model_card_content = model_card.content

        # Define the pattern for GitHub URLs
        url_pattern = r'https?://github\.com/[^\s/$.?#][^\s]*'
        links = re.findall(url_pattern, model_card_content)

        # Extract segments from model name
        model_parts = model_name.split('/')
        left_part = model_parts[0]
        right_part = model_parts[1] if len(model_parts) > 1 else ""

        # Split left and right parts by '-' and '_'
        left_sub_parts = re.split(r'[-_]', left_part)
        right_sub_parts = re.split(r'[-_]', right_part)

        # Collect all segments from left_sub_parts and the first segment from right_sub_parts into search_terms
        search_terms = set(left_sub_parts + [right_sub_parts[0]])

        # Attempt to find matches using the search terms
        for link in links:
            # Clean up the GitHub link (if needed)
            cleaned_link = re.sub(r'[).]+$', '', link)  # Remove trailing brackets and full stops
            cleaned_link = re.sub(r'[),]+$', '', cleaned_link)  # Remove trailing commas and other unwanted characters

            # Check if the link contains any of the search terms
            if any(term in cleaned_link for term in search_terms):
                github_links.add(cleaned_link)

        # Convert set to list and return only the first link if any
        github_links_list = list(github_links)
        if github_links_list:
            return [github_links_list[0]]
        else:
            return ["no_github"]

    else:
        return ["no_github"]

# Example usage with a DataFrame
#data_path = "/Users/adekunleajibode/Documents/transfering/sample.csv"
#output_path = "/Users/adekunleajibode/Documents/transfering/sample_github.csv"

data_path = "/home/local/SAIL/aajibode/paper_2/models_info.csv"
output_path = "/home/local/SAIL/aajibode/paper_2/modelGitHub.csv"

# Read the CSV file
df = pd.read_csv(data_path)

# Limit processing to first 100 rows for testing (change as needed)
small = df.iloc[:100]

# List to store GitHub links and their first 5 segments
github_links_list = []
github_first_5_segments = []

# Process each row in the DataFrame
for index, row in df.iterrows():  # Adjusted to use 'small' for testing purposes
    try:
        model_id = row['id']
        model_card = ModelCard.load(model_id)

        # Extract GitHub links using the defined function
        github_links = extract_links_from_card(model_card, model_id)

        # Append the GitHub links to the list
        github_links_list.extend(github_links)

        # Print the model ID and corresponding GitHub links
        print(f"{model_id} github is {github_links}")

    except Exception as e:
        # Handle errors loading ModelCard or extracting GitHub links
        print(f"Error extracting GitHub links for {model_id}: {e}")
        github_links_list.append("no_model_card")  # Append "no_model_card" for error cases

# Add the GitHub links list as a new column in the DataFrame
df['github_links'] = github_links_list

# Split the github_links by '/' and extract the first 5 elements if it's a valid GitHub link
df['cleaned_github'] = df['github_links'].apply(lambda x: '/'.join(x.split('/')[:5]) if isinstance(x, str) and x.startswith("https://github.com/") else x)

# Save the updated DataFrame to CSV
df.to_csv(output_path, index=False)

print("The output has successfully saved in a csv")
