import json
import pandas as pd
import re
import requests
from huggingface_hub import HfApi
from bs4 import BeautifulSoup
import unicodedata

tokens = "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"
api = HfApi(
    endpoint="https://huggingface.co",  # Can be a Private Hub endpoint.
    token=tokens,  # Replace with your token.
)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Authorization': f'token {tokens}',
    'Accept': 'application/vnd.github.v3+json'
}

file = "/Users/adekunleajibode/Documents/all_NLP_models.csv"

df1 = pd.read_csv(file, encoding="windows-1252")
main_df = df1[(df1["cleaned_github"] != 'no_github') & (df1["cleaned_github"] != 'no_model_card')]


top = main_df[main_df['downloads'] >= 10000]

top_prime = top[(top["cleaned_github"] != 'no_github') & (top["cleaned_github"] != 'no_model_card')]

df = top_prime


def clean_message(message, max_length=32767):
    if not message:
        return ''
    message = unicodedata.normalize('NFKC', message)
    message = re.sub(r'<[^>]+>', '', message)
    message = re.sub(r'```.*?```', '', message, flags=re.DOTALL)
    message = re.sub(r'\s+', ' ', message).strip()
    if len(message) > max_length:
        message = message[:max_length]
    return message


"""def get_commit_files(owner, model_name, commit_sha):
    # Retrieve all files in the repository
    files = api.list_repo_files(model_name)
    file_names = [file for file in files]

    # Retrieve files specific to the commit
    commit_files = []
    for f in file_names:
        file_loc = f"https://huggingface.co/{model_name}/blob/main/{f}"
        response = requests.get(file_loc)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            ul_tag = soup.find('ul', class_='break-words font-mono text-sm')
            if ul_tag:
                li_tags = ul_tag.find_all('li')
                for li in li_tags:
                    strong_tag = li.find('strong')
                    if strong_tag and strong_tag.text.strip() == 'SHA256:':
                        sha256_value = li.text.split(':')[-1].strip()
                        commit_files.append(f)
                        break
    return commit_files"""


def get_commit_files(model_name, commit_sha):
    url = f"https://huggingface.co/{model_name}/commit/{commit_sha}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Authorization': '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'  # Replace with your token
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check the page structure and adjust class names if necessary
        file_elements = soup.find_all('a', class_='d2h-file-name')
        commit_files = [file_elem.get_text().strip() for file_elem in file_elements]

        if not commit_files:
            print(f"No files found for {model_name} with SHA {commit_sha}")

        return commit_files
    else:
        # Print status code and content for debugging
        print(
            f"Failed to retrieve commit files for {model_name} with SHA {commit_sha}. Status code: {response.status_code}")
        #print(f"Response content: {response.text}")
        return []


combined_data = []

for index, row in df.iterrows():
    try:
        owner = row['owner']
        model_name = row['model_name']
        created_at = row['created_at_main']
        last_updated = row['last_modified_main']
        downloads = row['downloads']
        likes = row['likes']
        library_name = row['library_name']
        pipeline_tag = row['pipeline_tag']
        cleaned_github = row['cleaned_github']

        commits = api.list_repo_commits(model_name)

        # Iterate through commits and combine with other data
        for commit in commits:
            cleaned_title = clean_message(commit.title)
            cleaned_message = clean_message(commit.message)
            sha = commit.commit_id
            commit_files = get_commit_files(model_name, sha)

            commit_info = {
                'owner': owner,
                'model_name': model_name,
                'created_at': created_at,
                'last_updated': last_updated,
                'downloads': downloads,
                'likes': likes,
                'library_name': library_name,
                'pipeline_tag': pipeline_tag,
                'cleaned_github': cleaned_github,
                'title': cleaned_title,
                'message': cleaned_message,
                'commit_id': sha,
                'date': commit.created_at.date().isoformat(),  # Extract date only
                'author': commit.authors[0] if commit.authors else 'Unknown',
                'files': ', '.join(commit_files),  # List of files as a comma-separated string
            }
            combined_data.append(commit_info)

        print(f"Done with {model_name} in index {index}")

    except Exception as e:
        print(f"Error extracting model data for {model_name}: {e}")

    #print(f"Don with {model_name} in index {index}")

# Create a DataFrame from combined_data
combined_df = pd.DataFrame(combined_data)

# Export combined data to a CSV file
csv_filename = "/Users/adekunleajibode/Documents/commit_for_top_models.csv"
combined_df.to_csv(csv_filename, index=False)

#print(combined_df)

print(f"Combined model commit information exported to {csv_filename}")
