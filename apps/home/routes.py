from flask import render_template, request,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.dataset_search.dataset import search_kaggle_datasets,get_dataset_metadata,datasets

# Import the existing blueprint
from apps.home import blueprint

# Modify the existing routes to include dataset search functionality
@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# New route for dataset search
@blueprint.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_term = request.form['search']

        # Search local (mock) datasets
        local_filtered_datasets = [dataset for dataset in datasets if search_term.lower() in dataset['source_name'].lower()]  # Modified comparison logic

        # Search Kaggle datasets
        kaggle_datasets = search_kaggle_datasets(search_term)  # Modified search term

        # Combine results from all sources
        all_datasets = local_filtered_datasets + kaggle_datasets
        total_results = len(all_datasets)

        if not all_datasets:
            print("No search results found for", search_term)
            return render_template('search_results.html', datasets=[], message="No datasets found matching your search term.")

        return render_template('search_results.html', total_results=total_results,datasets=all_datasets)
    else:
        # Handle GET request (render search form)
        return render_template('search_form.html')
    

# Helper function to extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
