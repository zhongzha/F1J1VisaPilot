import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# BASE_URL = "https://www.cmu.edu/oie/employment/"
# BASE_URL = "https://www.cmu.edu/oie/maintaining-status/"
BASE_URL = "https://www.cmu.edu/oie/travel/"

DOMAIN = "www.cmu.edu"
VISITED = set()
OUTPUT_DIR = "cmu_oie_scrape"
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
SLEEP_BETWEEN_REQUESTS = 1  # seconds

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == DOMAIN and parsed.scheme in ["http", "https"]

def get_filename_from_url(url):
    path = urlparse(url).path
    if path.endswith("/"):
        path += "index"
    filename = path.strip("/").replace("/", "_")
    return filename

def save_html(url, content):
    filename = get_filename_from_url(url)
    filepath = os.path.join(HTML_DIR, filename)

    if os.path.exists(filepath):
        print(f"[HTML] Already exists: {filename}")
        return
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"[HTML] Saved: {filename}")

def download_pdf(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        filename = get_filename_from_url(url)
        filepath = os.path.join(PDF_DIR, filename)

        if os.path.exists(filepath):
            print(f"[PDF] Already exists: {filename}")
            return

        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"[PDF] Saved: {filename}")
        
    except Exception as e:
        print(f"[PDF ERROR] Failed to download {url}: {e}")

def crawl(url):
    if url in VISITED:
        return
    VISITED.add(url)
    time.sleep(SLEEP_BETWEEN_REQUESTS)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        return

    html = response.text
    save_html(url, html)

    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(url, href)
        if not is_valid_url(full_url):
            continue
        if full_url.endswith(".pdf"):
            download_pdf(full_url)
        elif full_url.startswith(BASE_URL):
            crawl(full_url)

if __name__ == "__main__":
    # Start crawling from the base URL
    print(f"Starting crawl from {BASE_URL}...")

    # Start crawling
    crawl(BASE_URL)
    print(f"Crawl completed. Visited {len(VISITED)} URLs.")