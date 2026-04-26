"""
Dark Web Clone Detection - Web Dashboard
Flask-based web interface for the detection system
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file
from modules.tor_handle import TorHandler
from modules.darkweb_crawler import DarkWebCrawler
from modules.extractor import FeatureExtractor
from modules.model import CloneDetector
from modules.reporter import ReportGenerator

app = Flask(__name__)
app.secret_key = 'darkweb_clone_detection_secret_key_2026'

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
DATA_RAW_DIR = BASE_DIR / 'data' / 'raw'
FEATURES_DIR = BASE_DIR / 'data' / 'features'


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def status():
    """Check Tor connection status"""
    tor = TorHandler(proxy_port=9150)
    is_running = tor.is_tor_running()
    
    return jsonify({
        'tor_running': is_running,
        'status': 'online' if is_running else 'offline',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/crawl', methods=['POST'])
def crawl():
    """Crawl a single .onion site"""
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    crawler = DarkWebCrawler(proxy_port=9150)
    
    # Check Tor first
    if not crawler.verify_connection():
        return jsonify({'error': 'Tor connection failed. Open Tor Browser first.'}), 500
    
    page_data = crawler.fetch_page(url)
    
    if page_data:
        filepath = crawler.save_page(page_data)
        return jsonify({
            'success': True,
            'title': page_data['title'],
            'size': page_data['html_length'],
            'time': page_data['response_time'],
            'file': str(filepath)
        })
    else:
        return jsonify({'error': 'Failed to crawl site'}), 500


@app.route('/api/compare', methods=['POST'])
def compare():
    """Compare two .onion sites"""
    data = request.get_json()
    url1 = data.get('url1', '')
    url2 = data.get('url2', '')
    
    if not url1 or not url2:
        return jsonify({'error': 'Both URLs are required'}), 400
    
    crawler = DarkWebCrawler(proxy_port=9150)
    
    # Check Tor
    if not crawler.verify_connection():
        return jsonify({'error': 'Tor connection failed. Open Tor Browser first.'}), 500
    
    # Crawl first site
    data1 = crawler.fetch_page(url1)
    if not data1:
        return jsonify({'error': f'Failed to crawl: {url1}'}), 500
    
    time.sleep(15)
    
    # Crawl second site
    data2 = crawler.fetch_page(url2)
    if not data2:
        return jsonify({'error': f'Failed to crawl: {url2}'}), 500
    
    # Save crawled data
    crawler.save_page(data1)
    crawler.save_page(data2)
    
    # Extract features
    extractor = FeatureExtractor()
    features1 = extractor.extract_all(data1['html'], data1['title'])
    features2 = extractor.extract_all(data2['html'], data2['title'])
    
    # Detect clone
    detector = CloneDetector(threshold=0.85)
    result = detector.compare(features1, features2)
    
    # Generate report
    reporter = ReportGenerator()
    report = reporter.generate(
        original_url=url1,
        suspect_url=url2,
        original_data=data1,
        suspect_data=data2,
        detection_result=result
    )
    
    # Save reports
    json_path = reporter.save_json(report)
    html_path = reporter.save_html(report)
    
    # Build response
    return jsonify({
        'success': True,
        'similarity_score': result.get('similarity_score', 0),
        'is_clone': result.get('is_clone', False),
        'verdict': result.get('verdict', ''),
        'risk_level': report['summary']['risk_level'],
        'original_title': data1['title'],
        'suspect_title': data2['title'],
        'original_size': data1['html_length'],
        'suspect_size': data2['html_length'],
        'breakdown': result.get('breakdown', []),
        'report_html': str(html_path),
        'report_json': str(json_path)
    })


@app.route('/api/history')
def history():
    """Get list of past detection results"""
    results = []
    
    if FEATURES_DIR.exists():
        for f in FEATURES_DIR.glob('detection_result_*.json'):
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                results.append({
                    'file': f.name,
                    'date': f.stat().st_mtime,
                    'original_url': data.get('original_url', ''),
                    'suspect_url': data.get('suspect_url', ''),
                    'score': data.get('similarity_score', 0),
                    'verdict': data.get('verdict', ''),
                    'is_clone': data.get('is_clone', False)
                })
    
    results.sort(key=lambda x: x['date'], reverse=True)
    
    # Convert timestamps
    for r in results:
        r['date'] = datetime.fromtimestamp(r['date']).strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({'results': results[:20]})  # Last 20


@app.route('/api/saved-pages')
def saved_pages():
    """Get list of crawled pages"""
    pages = []
    
    if DATA_RAW_DIR.exists():
        for f in DATA_RAW_DIR.glob('page_*.json'):
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                pages.append({
                    'file': f.name,
                    'url': data.get('url', ''),
                    'title': data.get('title', ''),
                    'size': data.get('html_length', 0),
                    'date': f.stat().st_mtime
                })
    
    pages.sort(key=lambda x: x['date'], reverse=True)
    
    for p in pages:
        p['date'] = datetime.fromtimestamp(p['date']).strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({'pages': pages})


@app.route('/api/compare-saved', methods=['POST'])
def compare_saved():
    """Compare two already-crawled pages"""
    data = request.get_json()
    file1 = data.get('file1', '')
    file2 = data.get('file2', '')
    
    if not file1 or not file2:
        return jsonify({'error': 'Both files are required'}), 400
    
    path1 = DATA_RAW_DIR / file1
    path2 = DATA_RAW_DIR / file2
    
    if not path1.exists() or not path2.exists():
        return jsonify({'error': 'File not found'}), 404
    
    # Load pages
    with open(path1, 'r', encoding='utf-8') as f:
        page1 = json.load(f)
    with open(path2, 'r', encoding='utf-8') as f:
        page2 = json.load(f)
    
    # Extract features
    extractor = FeatureExtractor()
    features1 = extractor.extract_all(page1['html'], page1['title'])
    features2 = extractor.extract_all(page2['html'], page2['title'])
    
    # Detect
    detector = CloneDetector()
    result = detector.compare(features1, features2)
    
    # Generate report
    reporter = ReportGenerator()
    report = reporter.generate(
        original_url=page1.get('url', ''),
        suspect_url=page2.get('url', ''),
        original_data=page1,
        suspect_data=page2,
        detection_result=result
    )
    
    json_path = reporter.save_json(report)
    html_path = reporter.save_html(report)
    
    return jsonify({
        'success': True,
        'similarity_score': result.get('similarity_score', 0),
        'is_clone': result.get('is_clone', False),
        'verdict': result.get('verdict', ''),
        'risk_level': report['summary']['risk_level'],
        'breakdown': result.get('breakdown', []),
        'report_html': str(html_path)
    })


@app.route('/reports/<filename>')
def serve_report(filename):
    """Serve generated report files"""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        return send_file(filepath)
    return "File not found", 404


if __name__ == '__main__':
    # Create template folder
    template_dir = Path(__file__).parent / 'templates'
    template_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("🌐 DARK WEB CLONE DETECTION DASHBOARD")
    print("=" * 60)
    print("\n📡 Starting web server...")
    print("🔗 Open this URL in your browser:")
    print("   http://127.0.0.1:5000")
    print("\n⚠️  Make sure Tor Browser is open!")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)