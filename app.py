from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_papers():
    search_term = request.form.get('term')

    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400

    # Construct the PubMed API URL with the search term
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    url = f'{base_url}?db=pubmed&term={search_term}&retmode=json'

    try:
        # Make the request to the PubMed API to get the PubMed IDs
        response = requests.get(url)
        response.raise_for_status()

        # Extract the PubMed IDs from the API response
        data = response.json()
        pubmed_ids = data['esearchresult']['idlist']

        article_details = []

        # Retrieve article details using the PubMed API's esummary endpoint
        for pubmed_id in pubmed_ids:
            summary_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json'
            summary_response = requests.get(summary_url)
            summary_response.raise_for_status()

            summary_data = summary_response.json()
            article_title = summary_data['result'][pubmed_id]['title']

            article_details.append({
                'pubmed_id': pubmed_id,
                'title': article_title
            })

        return render_template('results.html', article_details=article_details)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
