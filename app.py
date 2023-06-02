from flask import Flask, request, jsonify, render_template
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST', 'GET'])
def search_papers():
    search_term = request.form.get('term')
    page = int(request.form.get('page', 1)) if request.form.get('page') else 1

    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400

    # Construct the PubMed API URL with the search term and page
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    url = f'{base_url}?db=pubmed&term={search_term}&retmode=json&retstart={((page - 1) * 10)}&retmax=10'

    try:
        # Make the request to the PubMed API to get the PubMed IDs
        response = requests.get(url)
        response.raise_for_status()

        # Extract the PubMed IDs from the API response
        data = response.json()
        pubmed_ids = data['esearchresult']['idlist']
        total_results = int(data['esearchresult']['count'])
        total_pages = (total_results // 10) + 1

        article_details = []

        # Retrieve article details using the PubMed API's esummary endpoint
        for pubmed_id in pubmed_ids:
            summary_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json'
            summary_response = requests.get(summary_url)
            summary_response.raise_for_status()

            summary_data = summary_response.json()
            article_title = summary_data['result'][pubmed_id]['title']
            article_url = f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'

            # Get the authors' information
            authors = summary_data['result'][pubmed_id]['authors']
            author_names = [author['name'] for author in authors]

            article_details.append({
                'pubmed_id': pubmed_id,
                'title': article_title,
                'url': article_url,
                'authors': author_names
            })

        return render_template('results.html', article_details=article_details, page=page, total_pages=total_pages)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/abstract/<pubmed_id>')
def abstract(pubmed_id):
    # Construct the PubMed API URL to fetch the abstract
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    url = f'{base_url}?db=pubmed&id={pubmed_id}&retmode=xml'

    try:
        # Make the request to the PubMed API to get the article details
        response = requests.get(url)
        response.raise_for_status()

        # Parse the XML response
        xml_data = response.text
        root = ET.fromstring(xml_data)

        # Find the abstract element
        abstract_element = root.find('.//AbstractText')

        if abstract_element is not None:
            abstract = abstract_element.text.strip()
            return jsonify({'abstract': abstract})
        else:
            return jsonify({'abstract': 'Abstract Not Found'})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except ET.ParseError as e:
        return jsonify({'error': 'Error parsing XML response'}), 500


if __name__ == '__main__':
    app.run()
