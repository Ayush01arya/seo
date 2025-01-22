from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse
import time
import concurrent.futures
from datetime import datetime, timedelta
import ssl
import socket
from fake_useragent import UserAgent
import random
app = Flask(__name__)


def get_load_time(url):
    try:
        start = time.time()
        requests.get(url)
        return round(time.time() - start, 2)
    except:
        return 0


def get_ssl_info(url):
    domain = urlparse(url).netloc
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            return ssock.getpeercert()


def analyze_webpage(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Content analysis
    content_types = {
        'articles': len(soup.find_all('article')),
        'images': len(soup.find_all('img')),
        'videos': len(soup.find_all(['video', 'iframe'])),
        'forms': len(soup.find_all('form'))
    }

    # Extract metadata
    meta_tags = soup.find_all('meta')
    meta_data = {
        'title': soup.title.string if soup.title else '',
        'description': next((tag['content'] for tag in meta_tags if tag.get('name', '').lower() == 'description'), ''),
        'keywords': next((tag['content'] for tag in meta_tags if tag.get('name', '').lower() == 'keywords'), '')
    }

    seo_data = {
        'meta_title': soup.title.string if soup.title else '',
        'meta_description': next((tag['content'] for tag in soup.find_all('meta', {'name': 'description'})), ''),
        'h1_tags': [h1.text.strip() for h1 in soup.find_all('h1')],
        'h2_tags': [h2.text.strip() for h2 in soup.find_all('h2')],
        'img_alt_tags': len([img for img in soup.find_all('img') if img.get('alt')]),
        'total_images': len(soup.find_all('img')),
        'internal_links': len([a for a in soup.find_all('a') if a.get('href', '').startswith('/')]),
        'external_links': len([a for a in soup.find_all('a') if a.get('href', '').startswith('http')])
    }

    return {
        'content_types': content_types,
        'meta_data': meta_data,
        'seo_data': seo_data
    }


def generate_traffic_trend():
    # Generate realistic traffic trend data for the last 12 months
    months = []
    current_date = datetime.now()

    for i in range(12):
        month_date = current_date - timedelta(days=30 * i)
        months.insert(0, {
            'month': month_date.strftime('%b %Y'),
            'visitors': int(50000 + (i * 5000) + (random.randint(-5000, 5000)))
        })

    return months


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Parallel processing of different analyses
        with concurrent.futures.ThreadPoolExecutor() as executor:
            load_time_future = executor.submit(get_load_time, url)
            webpage_future = executor.submit(analyze_webpage, url)
            ssl_future = executor.submit(get_ssl_info, url)

            load_time = load_time_future.result()
            webpage_data = webpage_future.result()
            ssl_data = ssl_future.result()

        # Generate analysis data
        analysis_data = {
            'domainAuthority': random.randint(20, 100),  # Replace with real API call
            'totalBacklinks': random.randint(1000, 100000),  # Replace with real API call
            'totalKeywords': random.randint(500, 5000),  # Replace with real API call
            'loadTime': load_time,
            'contentTypes': webpage_data['content_types'],
            'trafficSources': {
                'Organic': 45,
                'Direct': 25,
                'Social': 20,
                'Referral': 10
            },
            'trafficTrend': generate_traffic_trend(),
            'meta_data': webpage_data['meta_data'],
            'ssl_info': ssl_data
        }

        return jsonify(analysis_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)