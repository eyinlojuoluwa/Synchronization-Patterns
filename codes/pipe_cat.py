import pandas as pd

# Define the categories and their corresponding tags (with dashes)
categories = {
    "MULTIMODAL": ["image-text-to-text", "visual-question-answering", "document-question-answering"],
    "COMPUTER VISION": ["depth-estimation", "image-classification", "object-detection", "image-segmentation", "text-to-image", "image-to-text", "image-to-image", "image-to-video", "unconditional-image-generation", "video-classification", "text-to-video", "zero-shot-image-classification", "mask-generation", "zero-shot-object-detection", "text-to-3d", "image-to-3d", "image-feature-extraction"],
    "NLP": ["text-classification", "token-classification", "table-question-answering", "question-answering", "zero-shot-classification", "translation", "summarization", "feature-extraction", "text-generation", "text2text-generation", "fill-mask", "sentence-similarity"],
    "AUDIO": ["text-to-speech", "text-to-audio", "automatic-speech-recognition", "audio-to-audio", "audio-classification", "voice-activity-detection"],
    "TABULAR": ["tabular-classification", "tabular-regression", "time-series-forecasting"],
    "REINFORCEMENT LEARNING": ["reinforcement-learning", "robotics"],
    "OTHERS": ["graph-machine-learning"]
}

# Function to categorize pipeline tags
def categorize_tag(tag):
    for category, tags in categories.items():
        if tag in tags:
            return category
    return "NONE"  # Return "NONE" if no matching category is found

# Load the CSV file into a DataFrame
df = pd.read_csv('/Users/adekunleajibode/Documents/PAPER2_experiment_steps/all_models/models_info.csv')

# Apply the categorization function to the pipeline_tag column
df['pipeline_category'] = df['pipeline_tag'].apply(categorize_tag)

# Save the updated DataFrame to a new CSV file
df.to_csv('/Users/adekunleajibode/Documents/PAPER2_experiment_steps/all_models/models_info2.csv', index=False)

print("CSV file cleaned and saved as 'modelGitHub2.csv'.")
