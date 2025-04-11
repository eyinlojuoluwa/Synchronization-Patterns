import pandas as pd
import requests
from huggingface_hub import HfApi
import re


api = HfApi(
    endpoint="https://huggingface.co",  # Can be a Private Hub endpoint.
    token="token",  # Token is not persisted on the machine.
)

#data = "/home/local/SAIL/aajibode/paper_2/models_GitHub.csv"
data = "/home/local/SAIL/aajibode/paper_2/models_GitHub.csv"

df1 = pd.read_csv(data)
df = df1[df1['considered'] != 'No']
#df = df2[:3]

combined_data = []

# Iterate through each row in the filtered DataFrame
for index, row in df.iterrows():
    try:
        # Extract relevant information from the row
        owner = row['owner']
        model_name = row['model_name']
        created_at = row['created_at']
        downloads = row['downloads']
        likes = row['likes']
        library_name = row['library_name']
        pipeline_tag = row['pipeline_tag']
        cleaned_github = row['cleaned_github']

        # Fetch commits for the model
        commits = api.list_repo_commits(model_name)

        # Iterate through commits and combine with other data
        for commit in commits:
            cleaned_message = re.sub(r'^\s*[\r\n]+', '', commit.message)
            commit_info = {
                'owner': owner,
                'model_name': model_name,
                'created_at': created_at,
                'downloads': downloads,
                'likes': likes,
                'library_name': library_name,
                'pipeline_tag': pipeline_tag,
                'cleaned_github': cleaned_github,
                'title': commit.title,
                'date': commit.created_at.date().isoformat(),  # Extract date only
                'author': commit.authors[0] if commit.authors else 'Unknown',
                'message': cleaned_message.strip()
            }
            combined_data.append(commit_info)

        print(f"Done with {model_name}")

    except Exception as e:
        print(f"Error extracting model data for {model_name}: {e}")

# Create a DataFrame from combined_data
combined_df = pd.DataFrame(combined_data)

# Export combined data to a CSV file
csv_filename = "/home/local/SAIL/aajibode/paper_2/commits_using_API.csv"
combined_df.to_csv(csv_filename, index=False)

print(combined_df)

print(f"Combined model commit information exported to {csv_filename}")

