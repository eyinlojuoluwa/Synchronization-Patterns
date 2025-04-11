import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

# File paths
file1 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/reduced_columns_GH_commit.csv"
file2 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/reduced_columns_GH_issues.csv"
file3 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/reduced_columns_GH_pulls.csv"
file4 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/HF_commit_986.csv"
file5 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/HF_issues_986.csv"
file6 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/HF_pull_986.csv"

# Reading CSV files with latin1 encoding
GH_commit1 = pd.read_csv(file1, encoding='latin1')
GH_issues1 = pd.read_csv(file2, encoding='latin1')
GH_pull1 = pd.read_csv(file3, encoding='latin1')
HF_commit1 = pd.read_csv(file4, encoding='latin1')
HF_issue1 = pd.read_csv(file5, encoding='latin1')
HF_pull1 = pd.read_csv(file6, encoding='latin1')


GH_commit1 = GH_commit1[['owner', 'github', 'model_name', 'commit_date', 'family']]
GH_issues1 = GH_issues1[['owner', 'github', 'model_name', 'issue_date', 'family']]
GH_pull1 = GH_pull1[['owner', 'github', 'model_name', 'pr_date', 'family']]
HF_commit1 = HF_commit1[['owner', 'model_name', 'created_at', 'last_updated', 'date', 'family']]
HF_issue1 = HF_issue1[['owner', 'model_name', 'created_at', 'last_updated', 'pull_date', 'family']]
HF_pull1 = HF_pull1[['owner', 'model_name', 'created_at', 'last_updated', 'pull_date', 'family']]


def get_right_part(name):
    return name.split('/')[-1] if isinstance(name, str) else name

#owners = ['microsoft_Phi-3']
owners = [
    'yangheng_absa-model', 'asapp_sew', 'beomi_ko', 'bigcode_starcoder2', 'distilbert_distilbert',
    'google_byt5', 'McGill-NLP_LLM2Vec', 'microsoft_DialoGPT', 'nghuyong_ernie',
    'persiannlp_mt5', 'prithivida_grammar', 'protectai_deberta',
    'PrunaAI_MaziyarPanahi', 'rinna_japanese-gpt', 'shenzhi-wang_Llama3',
    'tohoku-nlp_japanese_bert', 'tsmatz_xlm-roberta', 'T-Systems-onsite_sentence-transformer',
    'tuner007_pegasus_paraphrase', 'valhalla/t5-models',
]

def filter_data_by_owner(owner):
    GH_commit = GH_commit1[GH_commit1["family"] == owner].copy()
    HF_commit = HF_commit1[HF_commit1['family'] == owner].copy()

    GH_issues = GH_issues1[GH_issues1["family"] == owner].copy()
    HF_issues = HF_issue1[HF_issue1['family'] == owner].copy()

    GH_pull = GH_pull1[GH_pull1["family"] == owner].copy()
    HF_pull = HF_pull1[HF_pull1['family'] == owner].copy()

    # Convert to datetime and handle missing values
    GH_commit['commit_date'] = pd.to_datetime(GH_commit['commit_date'], errors='coerce').dt.date
    HF_commit['date'] = pd.to_datetime(HF_commit['date'], errors='coerce').dt.date
    GH_issues['issue_date'] = pd.to_datetime(GH_issues['issue_date'], errors='coerce').dt.date
    HF_issues['pull_date'] = pd.to_datetime(HF_issues['pull_date'], errors='coerce').dt.date
    GH_pull['pr_date'] = pd.to_datetime(GH_pull['pr_date'], errors='coerce').dt.date
    HF_pull['pull_date'] = pd.to_datetime(HF_pull['pull_date'], errors='coerce').dt.date

    # Apply the function to HuggingFace data
    HF_commit['model_name'] = HF_commit['model_name'].apply(get_right_part)
    HF_issues['model_name'] = HF_issues['model_name'].apply(get_right_part)
    HF_pull['model_name'] = HF_pull['model_name'].apply(get_right_part)

    # For GitHub activities, add fixed labels
    GH_commit['model_name'] = 'GH Commit'
    GH_issues['model_name'] = 'GH Issue'
    GH_pull['model_name'] = 'GH Pull Request'

    # Combine the data
    commit_data = pd.concat([HF_commit[['date', 'model_name']],
                             GH_commit[['commit_date', 'model_name']].rename(columns={'commit_date': 'date'})],
                            ignore_index=True)

    issue_data = pd.concat([HF_issues[['pull_date', 'model_name']].rename(columns={'pull_date': 'date'}),
                            GH_issues[['issue_date', 'model_name']].rename(columns={'issue_date': 'date'})],
                           ignore_index=True)

    pull_data = pd.concat([HF_pull[['pull_date', 'model_name']].rename(columns={'pull_date': 'date'}),
                           GH_pull[['pr_date', 'model_name']].rename(columns={'pr_date': 'date'})],
                          ignore_index=True)

    # Ensure only one activity per day by grouping and taking the first activity per day
    commit_data = commit_data.groupby(['date', 'model_name']).first().reset_index()
    issue_data = issue_data.groupby(['date', 'model_name']).first().reset_index()
    pull_data = pull_data.groupby(['date', 'model_name']).first().reset_index()

    # Sort to ensure GitHub activities appear before the variants
    commit_data['is_github'] = commit_data['model_name'].str.contains('GH')
    issue_data['is_github'] = issue_data['model_name'].str.contains('GH')
    pull_data['is_github'] = pull_data['model_name'].str.contains('GH')

    # Sort by the 'is_github' column (True first, then False)
    commit_data = commit_data.sort_values(by='is_github', ascending=True).drop(columns='is_github')
    issue_data = issue_data.sort_values(by='is_github', ascending=True).drop(columns='is_github')
    pull_data = pull_data.sort_values(by='is_github', ascending=True).drop(columns='is_github')

    return commit_data, issue_data, pull_data


# Function to set biweekly ticks
def set_biweekly_ticks(ax, data):
    start_date = data['date'].min()
    end_date = data['date'].max()
    ticks = pd.date_range(start=start_date, end=end_date, freq='2W')
    ax.set_xticks(ticks)
    week_labels = [f'Wk{i * 2 + 2}' for i in range(0, len(ticks))]
    ax.set_xticklabels(week_labels, rotation=90)


# Function to plot the activity for each owner
def plot_activity(ax, data, title, y_label):
    data = data.dropna(subset=['date'])  # Ensure there are no missing date values
    if not data.empty:
        colors = data['model_name'].apply(lambda x: 'blue' if 'GH' in x else 'orange')
        ax.scatter(data['date'], data['model_name'], color=colors, alpha=0.6)
        ax.set_title(title)
        ax.set_ylabel(y_label)
        set_biweekly_ticks(ax, data)
    else:
        ax.set_title(title)
        ax.set_ylabel(y_label)
        ax.set_xticks([])  # Remove x-ticks for empty plots


for owner in owners:
    commit_data, issue_data, pull_data = filter_data_by_owner(owner)

    fig, axes = plt.subplots(3, 1, figsize=(15, 10))  # One column, three rows for each owner

    # Plot Commits
    plot_activity(axes[0], commit_data, f'Commits Timeline ({owner})', 'Hugging Face / GitHub Commits')

    # Plot Issues
    plot_activity(axes[1], issue_data, f'Issues Timeline ({owner})', 'Hugging Face / GitHub Issues')

    # Plot Pull Requests
    plot_activity(axes[2], pull_data, f'Pull Requests Timeline ({owner})', 'Hugging Face / GitHub Pull Requests')

    # Set x-axis label only on the last row
    axes[2].set_xlabel('Date')
    #print(commit_data)

    plt.tight_layout()
    plt.show()