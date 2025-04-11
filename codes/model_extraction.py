import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_page(page_num, fetched_models):
    base_url = "https://huggingface.co/models?sort=trending&p="
    url = base_url + str(page_num)
    print(f"Fetching models from page {page_num}...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        models_data = []

        model_elements = soup.find_all('h4', class_='text-md truncate font-mono text-black dark:group-hover/repo:text-yellow-500 group-hover/repo:text-indigo-600 text-smd')
        if not model_elements:
            print(f"No more models found on page {page_num}.")
            return models_data

        for model in model_elements:
            model_name = model.text.strip()
            if '/' in model_name:
                owner, model_name = model_name.split('/', 1)
            else:
                print(f"Invalid model name format: {model_name}")
                continue

            # Skip if model has already been fetched
            if (owner, model_name) in fetched_models:
                continue
            
            # Add model to fetched set
            fetched_models.add((owner, model_name))

            pipeline_tag_element = model.find_next('div', class_='mr-1 flex items-center overflow-hidden whitespace-nowrap text-sm leading-tight text-gray-400')
            if pipeline_tag_element:
                pipeline_tag = pipeline_tag_element.text.strip().split('•')[0].strip()
            else:
                pipeline_tag = 'Unknown'

            models_data.append({
                'owner': owner.strip(),
                'model_name': model_name.strip(),
                'pipeline': pipeline_tag
            })

        return models_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        return []

def extract_models_and_pipelines(total_pages=24152, checkpoint_interval=1000, checkpoint_file='/home/local/SAIL/aajibode/paper_2/checkpoint.csv', output_file='/home/local/SAIL/aajibode/paper_2/all_models.csv'):
    fetched_models = set() 
    models_data = []

    # Load existing data if checkpoint file exists
    if os.path.exists(checkpoint_file):
        df_checkpoint = pd.read_csv(checkpoint_file)
        fetched_models.update(set(zip(df_checkpoint['owner'], df_checkpoint['model_name'])))
        models_data.extend(df_checkpoint.to_dict('records'))
        start_page = len(df_checkpoint) // 30 + 1
        print(f"Resuming from page {start_page} based on checkpoint.")
    else:
        start_page = 0  # Pagination starts at 0 for the first page

    with ThreadPoolExecutor(max_workers=30) as executor:  # Adjust the number of workers as needed
        futures = [executor.submit(fetch_page, page_num, fetched_models) for page_num in range(start_page, total_pages)]
        
        for i, future in enumerate(as_completed(futures)):
            try:
                page_models = future.result()
                print(f"Fetched {len(page_models)} models from a page.")
                models_data.extend(page_models)
                if len(models_data) % checkpoint_interval == 0:
                    save_to_csv(models_data, checkpoint_file)
                    print(f"Checkpoint saved after fetching {len(models_data)} models.")
            except Exception as e:
                print(f"Error processing a page: {e}")

    save_to_csv(models_data, output_file)  # Save final data to output file
    return models_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Example usage:
if __name__ == "__main__":
    start_time = time.time()
    checkpoint_file = '/home/local/SAIL/aajibode/paper_2/checkpoint.csv'
    output_file = '/home/local/SAIL/aajibode/paper_2/all_models.csv'
    models_data = extract_models_and_pipelines(total_pages=24152, checkpoint_interval=1000, checkpoint_file=checkpoint_file, output_file=output_file)
    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")
    print(f"Total unique models fetched: {len(models_data)}")
