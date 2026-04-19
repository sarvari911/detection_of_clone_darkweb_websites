import requests
import os

def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_html(content, filename):
    os.makedirs("data/raw", exist_ok=True)
    with open(f"data/raw/{filename}", "w", encoding="utf-8") as f:
        f.write(content)

def crawl(url1, url2):
    html1 = fetch_html(url1)
    html2 = fetch_html(url2)

    if html1:
        save_html(html1, "site1.html")

    if html2:
        save_html(html2, "site2.html")

    print("Crawling complete ✅")