from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/abstract/<pubmed_id>')
def abstract(pubmed_id):
    # Construct the PubMed API URL to fetch the article details
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


@app.route('/keywords/<pubmed_id>')
def keywords(pubmed_id):
    # Construct the PubMed API URL to fetch the keywords
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    url = f'{base_url}?db=pubmed&id={pubmed_id}&retmode=xml'

    try:
        # Make the request to the PubMed API to get the article details
        response = requests.get(url)
        response.raise_for_status()

        # Parse the XML response
        xml_data = response.text
        root = ET.fromstring(xml_data)

        # Find the keyword elements
        keyword_elements = root.findall('.//Keyword')

        keywords = []
        if keyword_elements:
            keywords = [keyword.text.strip() for keyword in keyword_elements]

        return jsonify({'keywords': keywords})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except ET.ParseError as e:
        return jsonify({'error': 'Error parsing XML response'}), 500


if __name__ == '__main__':
    app.run(debug=True)
