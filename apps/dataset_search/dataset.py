from flask import Flask, render_template, request,url_for
import kaggle
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Mock dataset data (optional, you can remove this if you have real data)
datasets = [
    {'source_name': 'Source A (Nepal)', 'source_link': 'http://example.com/sourceA', 'file_format': 'CSV', 'author': 'Author A', 'description': 'Dataset A description about Nepal', 'updated': '2024-01-01', 'time_period': '2020-2022', 'area_covered': 'Nepal', 'topic': 'Engineering'},
    {'source_name': 'Source B (Not Nepal)', 'source_link': 'http://example.com/sourceB', 'file_format': 'JSON', 'author': 'Author B', 'description': 'Dataset B description (not about Nepal)', 'updated': '2023-01-01', 'time_period': '2018-2020', 'area_covered': 'Europe', 'topic': 'Humanities'},
]

def get_dataset_metadata(dataset_url):
    response = requests.get(dataset_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    metadata = {}

    # Extract metadata from the dataset page
    source_name_elem = soup.find(class_='ProfileHeader__displayName')
    metadata['source_name'] = source_name_elem.text.strip() if source_name_elem else None

    source_link_elem = soup.find('link', rel='canonical')
    metadata['source_link'] = source_link_elem.get('href') if source_link_elem else None

    author_elem = soup.find(class_='ProfileHeader__detailsItem--link')
    metadata['author'] = author_elem.text.strip() if author_elem else None

    return metadata

def search_kaggle_datasets(query):
    try:
        kaggle.api.authenticate()  # Authenticate if not already done
    except NameError:
        print("Kaggle API not authenticated. Please authenticate before searching.")
        return []

    search_results = kaggle.api.dataset_list(search=query)  # Use provided query for search

    datasets_with_metadata = []

    for dataset in search_results:
        # Search based on provided query, ignoring case for flexibility
        if query.lower() in dataset.title.lower():  # Modified comparison logic
            dataset_metadata = get_dataset_metadata(dataset.url)
            dataset_with_metadata = {
                "title": dataset.title,
                "metadata": dataset_metadata
            }
            datasets_with_metadata.append(dataset_with_metadata)

    return datasets_with_metadata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_term = request.args.get('search')  # Access search term from query string
    page = int(request.args.get('page', 1)) 
    if request.method == 'POST':
        search_term = request.form['search']

        # Search local (mock) datasets
        local_filtered_datasets = [dataset for dataset in datasets if search_term.lower() in dataset['source_name'].lower()]  # Modified comparison logic

        # Search Kaggle datasets
        kaggle_datasets = search_kaggle_datasets(search_term)  # Modified search term

# Combine results from all sources
        all_datasets = local_filtered_datasets + kaggle_datasets
        total_results = len(all_datasets)

        # Pagination logic (assuming results per page is 5)
        page = int(request.args.get('page', 1))  # Get current page from query string (default 1)
        results_per_page = 5
        start_index = (page - 1) * results_per_page
        end_index = start_index + results_per_page
        page_data = all_datasets[start_index:end_index]  # Get results for current page

        # Pagination links (improved URL construction)
        prev_page_url = None
        next_page_url = None
        if page > 1:
            prev_page_url = url_for('search', page=page - 1)  # Use `url_for` for correct URLs
        if total_results > end_index:
            next_page_url = url_for('search', page=page + 1)

        if not all_datasets:
            print("No search results found for", search_term)
            return render_template('search_results.html', datasets=[], message="No datasets found matching your search term.")

        return render_template('search_results.html', datasets=page_data, total_results=total_results, prev_page_url=prev_page_url, next_page_url=next_page_url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
