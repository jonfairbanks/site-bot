import requests, time
from bs4 import BeautifulSoup

session = requests.Session()

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
}


def scrape_url(url, HISTORY):
    try:
        start_time = time.time()
        response = session.get(url, headers=headers, allow_redirects=True, timeout=5)
        elapsed_time = time.time() - start_time

        HISTORY.append((url, elapsed_time))

        if response.status_code == 200:
            data = BeautifulSoup(response.text, "html.parser")
        else:
            data = None
    except Exception:
        data = None
    return data
