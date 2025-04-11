import pandas as pd
import time
from github import Github, RateLimitExceededException, BadCredentialsException, UnknownObjectException, GithubException
import requests

import re

access_token = "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"


#file = "D:/Paper2/PAPER2_experiment_steps/NLP/all_NLP_models.csv"

file = "C:/paper2_home/all_NLP_models.csv"



df1 = pd.read_csv(file, encoding='latin1')



main_df = df1[(df1["cleaned_github"] != 'no_github') & (df1["cleaned_github"] != 'no_model_card')]


top = main_df[main_df['downloads'] >= 10000]
bottom = main_df[main_df['downloads'] < 10000]

top_prime = top[(top["cleaned_github"] != 'no_github') & (top["cleaned_github"] != 'no_model_card')]
bottom_prime = top[~((top["cleaned_github"] != 'no_github') & (top["cleaned_github"] != 'no_model_card'))]

df_m = top_prime.groupby("cleaned_github").agg({
    'owner' : lambda x: x.unique(),
    'model_name' : 'nunique',
    'pipeline_tag' :  'unique',
    'library_name' : 'unique',
    'downloads' : 'mean',
    'likes' : 'mean',
}).reset_index()

#df4 = pd.DataFrame(df, index=None)

df = df_m


# Prepare lists to store results and errors
results = []
errors = []

def check_rate_limit(github_client):
    rate_limit = github_client.get_rate_limit()
    remaining = rate_limit.core.remaining
    reset_timestamp = rate_limit.core.reset.timestamp()
    current_timestamp = time.time()
    limit = rate_limit.core.limit
    print(f"Rate limit: {remaining} / {limit}")  # Debug print statement

    if remaining < 5:
        print(f"Rate limit nearing. Sleeping for 1800 seconds.")
        time.sleep(1800)

    #if remaining == 0:
        #sleep_time = reset_timestamp - current_timestamp
        #if sleep_time > 0:
            #print(f"Rate limit reached. Sleeping for {int(sleep_time)} seconds.")
            #time.sleep(sleep_time + 10)  # Adding a buffer to ensure reset is complete


def remove_tracebacks(message):
    # Remove traceback patterns
    return re.sub(r'Traceback \(most recent call last\):.*?(?=\n\n|$)', '', message, flags=re.DOTALL)

def remove_html_tags(message):
    # Remove HTML tags
    return re.sub(r'<[^>]+>', '', message)

def remove_code_snippets(message):
    # Remove code snippets (assuming they are wrapped in backticks or similar)
    return re.sub(r'```.*?```', '', message, flags=re.DOTALL)

def clean_commit_message(message, max_length=32767):
    message = remove_tracebacks(message)
    message = remove_html_tags(message)
    message = remove_code_snippets(message)
    # Optionally, remove excessive newlines and whitespace
    message = re.sub(r'\s+', ' ', message).strip()
    if len(message) > max_length:
        message = message[:max_length]
    return message

def fetch_commits(repo_owner, repo_name, other_data):
    global results, errors
    g = Github(access_token, retry=10, timeout=15, per_page=100)
    print(f'Extracting commits from {repo_owner}/{repo_name} repo')

    try:
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
        commits = repo.get_commits()
        tags = list(repo.get_tags())

        for commit in commits:
            try:
                check_rate_limit(g)

                author_name = commit.commit.author.name if commit.commit and commit.commit.author and commit.commit.author.name else "Unknown"
                author_username = commit.author.login if commit.author else "Unknown"
                author_profile_url = f"https://github.com/{author_username}" if commit.author else "Unknown"
                author_email = commit.commit.author.email if commit.commit and commit.commit.author and commit.commit.author.email else "Unknown"
                commit_message = clean_commit_message(commit.commit.message)
                commit_url = commit.html_url
                commit_date = commit.commit.author.date if commit.commit and commit.commit.author else "Unknown"
                commit_id = commit.sha
                commit_files = [file.filename for file in commit.files] if commit.files else []
                commit_tags = [tag.name for tag in tags if tag.commit.sha == commit.sha]
                committer_name = commit.commit.committer.name if commit.commit and commit.commit.committer and commit.commit.committer.name else "Unknown"
                committer_username = commit.committer.login if commit.committer else "Unknown"
                committer_profile_url = f"https://github.com/{committer_username}" if commit.committer else "Unknown"
                committer_date = commit.commit.committer.date if commit.commit and commit.commit.committer else "Unknown"
                parent_commits = [parent.sha for parent in commit.parents] if commit.parents else []
                commit_statuses = commit.get_statuses()
                statuses = [(status.context, status.state) for status in commit_statuses]
                commit_comments = commit.get_comments()
                comments = [(comment.user.login, comment.body) for comment in commit_comments]
                is_merge_commit = commit.commit.message.startswith("Merge") if commit.commit else False
                commit_tree_sha = commit.commit.tree.sha if commit.commit and commit.commit.tree else "Unknown"

                results.append({
                    **other_data,
                    "author_name": author_name,
                    "author_username": author_username,
                    "author_profile_url": author_profile_url,
                    "author_email": author_email,
                    "commit_message": commit_message,
                    "commit_id": commit_id,
                    "commit_url": commit_url,
                    "commit_date": commit_date,
                    "commit_files": commit_files,
                    "commit_tags": commit_tags,
                    "committer_name": committer_name,
                    "committer_username": committer_username,
                    "committer_profile_url": committer_profile_url,
                    "committer_date": committer_date,
                    "parent_commits": parent_commits,
                    "commit_statuses": statuses,
                    "commit_comments": comments,
                    "is_merge_commit": is_merge_commit,
                    "commit_tree_sha": commit_tree_sha,
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
    github = row['cleaned_github']
    owner = row['owner']
    model_name = row['model_name']
    pipeline_tag = row['pipeline_tag']
    library_name = ['library_name']
    downloads = ['downloads']
    likes = ['likes']

    repo_owner, repo_name = github.rstrip('/').split('/')[-2:]

    other_data = {
        "owner": owner,
        'github' : github,
        "model_name": model_name,
        "downloads": downloads,
        "likes": likes,
        "library_name": library_name,
        "pipeline_tag": pipeline_tag,

    }

    fetch_commits(repo_owner, repo_name, other_data)
    print(f"Done with {model_name} in index {index}")


# Convert results to DataFrame and save to CSV
results_df = pd.DataFrame(results)
results_df.to_csv("C:/paper2_home/GH_commits.csv", index=False)

# Convert errors to DataFrame and save to CSV
errors_df = pd.DataFrame(errors)
errors_df.to_csv("C:/paper2_home/github_commit_errors.csv", index=False)

print("Data collection complete.")
