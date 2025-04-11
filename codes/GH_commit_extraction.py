import pandas as pd
import time
from github import Github, RateLimitExceededException, BadCredentialsException, UnknownObjectException, GithubException
import requests

data = "/home/local/SAIL/aajibode/paper_2/models_GitHub.csv"

df1 = pd.read_csv(data)
df2 = df1[(df1['considered'] != 'No') & (df1['git_complete'] != 'notcorrect')]

# Drop duplicates based on the 'cleaned_github' column to get unique GitHub repositories
df_unique_repos = df2.drop_duplicates(subset='cleaned_github')

df = df_unique_repos  # Adjust the range as needed

# Define your GitHub token
access_token = "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"

# Prepare lists to store results and errors
results = []
errors = []

def check_rate_limit(github_client):
    rate_limit = github_client.get_rate_limit()
    remaining = rate_limit.core.remaining
    reset_timestamp = rate_limit.core.reset.timestamp()
    current_timestamp = time.time()

    if remaining == 0:
        sleep_time = reset_timestamp - current_timestamp
        if sleep_time > 0:
            print(f"Rate limit reached. Sleeping for {int(sleep_time)} seconds.")
            time.sleep(sleep_time + 10)  # Adding a buffer to ensure reset is complete

def fetch_commits(repo_owner, repo_name, other_data):
    global results, errors
    g = Github(access_token, retry=10, timeout=15, per_page=100)
    print(f'Extracting commits from {repo_owner}/{repo_name} repo')

    try:
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
        commits = repo.get_commits()

        for commit in commits:
            try:
                check_rate_limit(g)

                author_name = commit.commit.author.name if commit.commit and commit.commit.author and commit.commit.author.name else "Unknown"
                author_username = commit.author.login if commit.author else "Unknown"
                author_profile_url = f"https://github.com/{author_username}" if commit.author else "Unknown"
                commit_message = commit.commit.message
                commit_url = commit.html_url

                results.append({
                    **other_data,
                    "c_author_name": author_name,
                    "c_author_username": author_username,
                    "c_author_profile_url": author_profile_url,
                    "commit_message": commit_message,
                    "commit_url": commit_url
                })

            except RateLimitExceededException as e:
                print('Rate limit exceeded')
                time.sleep(300)
                errors.append({**other_data, "error_status": e.status, "error_message": "Rate limit exceeded"})
                continue
            except BadCredentialsException as e:
                print('Bad credentials exception')
                errors.append({**other_data, "error_status": e.status, "error_message": "Bad credentials"})
                break
            except UnknownObjectException as e:
                print('Unknown object exception')
                errors.append({**other_data, "error_status": e.status, "error_message": "Unknown object"})
                break
            except GithubException as e:
                print('General exception')
                errors.append({**other_data, "error_status": e.status, "error_message": "General exception"})
                break
            except requests.exceptions.ConnectionError as e:
                print('Retries limit exceeded')
                time.sleep(10)
                errors.append({**other_data, "error_status": "ConnectionError", "error_message": str(e)})
                continue
            except requests.exceptions.Timeout as e:
                print('Time out exception')
                time.sleep(10)
                errors.append({**other_data, "error_status": "Timeout", "error_message": str(e)})
                continue

    except RateLimitExceededException as e:
        print('Rate limit exceeded')
        time.sleep(300)
        errors.append({**other_data, "error_status": e.status, "error_message": "Rate limit exceeded"})
    except BadCredentialsException as e:
        print('Bad credentials exception')
        errors.append({**other_data, "error_status": e.status, "error_message": "Bad credentials"})
    except UnknownObjectException as e:
        print('Unknown object exception')
        errors.append({**other_data, "error_status": e.status, "error_message": "Unknown object"})
    except GithubException as e:
        print('General exception')
        errors.append({**other_data, "error_status": e.status, "error_message": "General exception"})
    except requests.exceptions.ConnectionError as e:
        print('Retries limit exceeded')
        time.sleep(10)
        errors.append({**other_data, "error_status": "ConnectionError", "error_message": str(e)})
    except requests.exceptions.Timeout as e:
        print('Time out exception')
        time.sleep(10)
        errors.append({**other_data, "error_status": "Timeout", "error_message": str(e)})

# Process each unique repository
for index, row in df.iterrows():
    owner = row['owner']
    model_name = row['model_name']
    created_at = row['created_at']
    downloads = row['downloads']
    likes = row['likes']
    library_name = row['library_name']
    pipeline_tag = row['pipeline_tag']
    cleaned_github = row['cleaned_github']

    repo_owner, repo_name = cleaned_github.rstrip('/').split('/')[-2:]

    other_data = {
        "owner": owner,
        "model_name": model_name,
        "created_at": created_at,
        "downloads": downloads,
        "likes": likes,
        "library_name": library_name,
        "pipeline_tag": pipeline_tag,
        "cleaned_github": cleaned_github
    }

    fetch_commits(repo_owner, repo_name, other_data)
    print(f"Done with {model_name} in index {index}")

# Convert results to DataFrame and save to CSV
results_df = pd.DataFrame(results)
results_df.to_csv("/home/local/SAIL/aajibode/paper_2/github_commits.csv", index=False)

# Convert errors to DataFrame and save to CSV
errors_df = pd.DataFrame(errors)
errors_df.to_csv("/home/local/SAIL/aajibode/paper_2/github_commit_errors.csv", index=False)

print("Data collection complete.")
