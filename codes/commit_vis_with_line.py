import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

# File paths
file1 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/reduced_columns_GH_commit.csv"
file2 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/HF_commit_986.csv"
file3 = "I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/sampled_families/manual_label_analysis/manually_sampled_result.csv"



# Reading CSV files with latin1 encoding
GH_commit1 = pd.read_csv(file1, encoding='latin1')
HF_commit1 = pd.read_csv(file2, encoding='latin1')
families = pd.read_csv(file3, encoding='latin1')




GH_commit1 = GH_commit1[['owner', 'github', 'model_name', 'commit_date', 'family']]
HF_commit1 = HF_commit1[['owner', 'model_name', 'created_at', 'last_updated', 'date', 'family']]

family = list(families['family'].unique())
print(family)




def get_right_part(name):
    return name.split('/')[-1] if isinstance(name, str) else name


owners = ['01-ai_YI']


def filter_data_by_owner(owner, GH_commit1, HF_commit1):
    GH_commit = GH_commit1[GH_commit1["family"] == owner].copy()
    HF_commit = HF_commit1[HF_commit1['family'] == owner].copy()

    # Convert to datetime and handle missing values
    GH_commit['commit_date'] = pd.to_datetime(GH_commit['commit_date'], errors='coerce').dt.tz_localize(None)
    HF_commit['date'] = pd.to_datetime(HF_commit['date'], format='%m/%d/%Y', errors='coerce').dt.tz_localize(None)

    # Apply the function to HuggingFace data
    HF_commit['model_name'] = HF_commit['model_name'].apply(get_right_part)

    # For GitHub activities, add fixed labels
    GH_commit['model_name'] = 'GH Commit'

    # Combine the data
    commit_data = pd.concat([HF_commit[['date', 'model_name']],
                             GH_commit[['commit_date', 'model_name']].rename(columns={'commit_date': 'date'})],
                            ignore_index=True)
    return commit_data


# Function to set biweekly ticks
def set_biweekly_ticks(ax, data):
    start_date = data['date'].min()
    end_date = data['date'].max()
    num_biweeks = (end_date - start_date).days // 14 + 1
    ticks = [start_date + timedelta(days=i * 14) for i in range(num_biweeks)]
    ax.set_xticks(ticks)

    # Add dashed lines for each biweek only if both GH commit and variant commit exist in that biweek
    for tick in ticks:
        # Check if there are both GH commits and variant commits in the current biweek
        gh_commit_in_biweek = not data[(data['date'] >= tick) & (data['date'] < tick + timedelta(days=14)) & (
                    data['model_name'] == 'GH Commit')].empty
        variant_commit_in_biweek = not data[(data['date'] >= tick) & (data['date'] < tick + timedelta(days=14)) & (
                    data['model_name'] != 'GH Commit')].empty

        # Only add a dashed line if both types of commits exist in the biweek
        if gh_commit_in_biweek and variant_commit_in_biweek:
            ax.axvline(x=tick, color='black', linestyle='--', alpha=0.1, linewidth=1)  # Longer and lighter dashed lines

    week_labels = [f'Wk{i * 2 + 2}' for i in range(len(ticks))]  # Start from Week 2
    ax.set_xticklabels(week_labels, rotation=90)


# Function to plot the activity for each owner
def plot_activity(ax, data, title, y_label):
    data = data.dropna(subset=['date'])  # Ensure there are no missing date values
    if not data.empty:
        # Create custom biweekly periods
        min_date = data['date'].min()
        data['biweek'] = (data['date'] - min_date).dt.days // 14

        # Group data by biweek and model_name
        grouped_data = data.groupby(['biweek', 'model_name']).first().reset_index()

        # Calculate the start date for each biweek
        grouped_data['biweek_start'] = min_date + pd.to_timedelta(grouped_data['biweek'] * 14, unit='D')

        colors = grouped_data['model_name'].apply(lambda x: 'blue' if x == 'GH Commit' else 'orange')
        ax.scatter(grouped_data['biweek_start'], grouped_data['model_name'], color=colors, alpha=0.6)
        ax.set_title(title)
        ax.set_ylabel(y_label)
        set_biweekly_ticks(ax, data)  # Set the ticks and dashed lines only where needed
    else:
        ax.set_title(title)
        ax.set_ylabel(y_label)
        ax.set_xticks([])  # Remove x-ticks for empty plots


# Plot for each owner
for owner in owners:
    commit_data = filter_data_by_owner(owner, GH_commit1, HF_commit1)

    fig, ax = plt.subplots(figsize=(12, 5))  # Create one plot per owner with one row
    plot_activity(ax, commit_data, f'Commits Timeline ({owner})', 'Hugging Face / GitHub Commits')

    ax.set_xlabel('Date')  # Set x-axis label

    plt.tight_layout()

    # Save the figure
    #save_path = f"I:/Paper2/PAPER2_experiment_steps/NLP/Experiment_for_top_models/all_dataset/sampled_families/manual_label_analysis/all_figures/{owner}_commits_timeline.png"
    #plt.savefig(save_path)  # Save each figure with the owner's name
    plt.show()