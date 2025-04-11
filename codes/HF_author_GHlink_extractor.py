import json
import pandas as pd
import re
import os
import requests
import numpy as np
from bs4 import BeautifulSoup

data = "/Users/adekunleajibode/Documents/PAPER2_experiment_steps/GitHub_models/commits_using_API.csv"
df = pd.read_csv(data)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


df['full_name'] = "None"
df['github_link'] = "None"

for index, row in df.iterrows():
    try:
        author = row['author']
        author_url = f"https://huggingface.co/{author}"
        author_response = requests.get(author_url, headers=headers)
        author_response.raise_for_status()

        author_soup = BeautifulSoup(author_response.content, "html.parser")

        full_name_element = author_soup.find("span", class_="mr-3 leading-6")
        full_name = full_name_element.text.strip() if full_name_element else 'None'

        github_link_element = author_soup.find("a", href=re.compile(r"https://github.com/"))
        github_link = github_link_element['href'] if github_link_element else 'None'

        # Update the DataFrame
        df.at[index, 'full_name'] = full_name
        df.at[index, 'github_link'] = github_link

        print(f"Done with the {author} at index {index}")

    except requests.exceptions.RequestException as e:
        print(f"Error extracting commit info for {author}: {e}")
    except Exception as e:
        print(f"Error extracting commit info for {author}: {e}")

print(df)
output_file = "/Users/adekunleajibode/Documents/PAPER2_experiment_steps/GitHub_models/updated_commits_using_API.csv"
df.to_csv(output_file, index=False)