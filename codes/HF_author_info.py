import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from ratelimit import limits, sleep_and_retry

data = "/Users/adekunleajibode/Documents/PAPER2_experiment_steps/GitHub_models/commit_supplementary.csv"
output_file = "/Users/adekunleajibode/Documents/PAPER2_experiment_steps/GitHub_models/updated_commit_supplementary.csv"
df = pd.read_csv(data)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Define rate limit: 500 requests per 120 seconds
@sleep_and_retry
@limits(calls=500, period=120)
def fetch_author_info(author):
    try:
        author_url = f"https://huggingface.co/{author}"
        author_response = requests.get(author_url, headers=headers)
        author_response.raise_for_status()

        author_soup = BeautifulSoup(author_response.content, "html.parser")

        full_name_element = author_soup.find("span", class_="mr-3 leading-6")
        full_name = full_name_element.text.strip() if full_name_element else 'None'

        github_link_element = author_soup.find("a", href=re.compile(r"https://github.com/"))
        github_link = github_link_element['href'] if github_link_element else 'None'

        return full_name, github_link

    except requests.exceptions.RequestException as e:
        print(f"Error extracting info for {author}: {e}")
        return 'None', 'None'
    except Exception as e:
        print(f"Error extracting info for {author}: {e}")
        return 'None', 'None'

# Process each row in the DataFrame
updates = []
for index, row in df.iterrows():
    author = row['author']
    full_name, github_link = fetch_author_info(author)
    updates.append((full_name, github_link))
    print(f"Done with {author} at index {index}")

    # Introduce a small delay between requests to avoid overwhelming the server
    time.sleep(0.5)  # Adjust as needed

# Update the DataFrame with all collected data
df['full_name'], df['github_link'] = zip(*updates)

# Save updated DataFrame to CSV
df.to_csv(output_file, index=False)

print("Processing completed. Updated data saved to:", output_file)
