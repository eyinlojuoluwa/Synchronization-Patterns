import pandas as pd
from huggingface_hub import HfApi
from datetime import date

# Hugging Face API token
hugging_token = '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'
api = HfApi(token=hugging_token)

# Path to your CSV file
file = "I:/Paper2/PAPER2_experiment_steps/NLP/no_creation_date.csv"

# Load the CSV file into a DataFrame
df = pd.read_csv(file, encoding='latin1')
#df = df1[0:10]  # Optionally limit to the first 10 rows

# Create new columns to store the first commit date (created_at) and last commit date (last_updated)
df['created_at'] = None
df['last_updated'] = None

# Iterate over the rows in the DataFrame
for index, row in df.iterrows():
    name = row['model_name']

    try:
        # List the repository commits
        commits = api.list_repo_commits(name)

        if commits:
            # Extract the first and last commit dates
            # Assuming created_at is in ISO format and needs conversion
            first_commit_date = pd.to_datetime(commits[-1].created_at).date()
            last_commit_date = pd.to_datetime(commits[0].created_at).date()

            # Update the DataFrame with the commit dates
            df.at[index, 'created_at'] = first_commit_date
            df.at[index, 'last_updated'] = last_commit_date

        else:
            print(f"No commits found for {name}")
            # Use today's date if no commits are found
            df.at[index, 'created_at'] = date.today()
            df.at[index, 'last_updated'] = date.today()

    except Exception as e:
        print(f"Error processing {name}: {e}")
        df.at[index, 'created_at'] = date.today()
        df.at[index, 'last_updated'] = date.today()

# Save the modified DataFrame back to a CSV file
df.to_csv("I:/Paper2/PAPER2_experiment_steps/NLP/no_creation_date_updated.csv", index=False)

# Optionally, print the first few rows to inspect the changes
print(df)
