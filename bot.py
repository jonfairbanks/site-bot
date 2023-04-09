import argparse
import json
import time
import concurrent.futures
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import hashlib


def scan_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        start_time = time.time()
        soup = BeautifulSoup(response.content, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]
        end_time = time.time()
        return {
            "url": url,
            "links": links,
            "time_taken": end_time - start_time,
            "html_content": response.content.decode(),
        }
    except requests.exceptions.RequestException:
        return {"url": url, "links": [], "time_taken": float("inf"), "html_content": ""}


def scan_domain(domain, max_depth=3):
    urls_to_scan = [f"http://{domain}/"]
    scanned_urls = set()
    results = []
    for depth in range(max_depth):
        new_urls_to_scan = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {
                executor.submit(scan_url, url): url for url in urls_to_scan
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    scanned_urls.add(url)
                    new_urls_to_scan.extend(
                        link
                        for link in result["links"]
                        if link not in scanned_urls
                        and urlparse(link).hostname == domain
                    )
                except Exception as exc:
                    print(f"Exception while scanning {url}: {exc}")
        urls_to_scan = new_urls_to_scan
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scan a list of domains for outbound links."
    )
    parser.add_argument(
        "domains", metavar="DOMAIN", nargs="+", help="the domains to scan"
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        metavar="DEPTH",
        type=int,
        default=3,
        help="the maximum depth to follow links",
    )
    args = parser.parse_args()

    results = []
    for domain in args.domains:
        results.extend(scan_domain(domain, args.max_depth))

    with open("results.json", "w") as f:
        json.dump(results, f)

    with open("html_contents.json", "w") as f:
        for result in results:
            if result["html_content"]:
                url_hash = hashlib.md5(result["url"].encode()).hexdigest()
                f.write(f"{url_hash}.html\n")
                with open(f"{url_hash}.html", "w") as html_file:
                    html_file.write(result["html_content"])

    times = {}
    for result in results:
        domain = urlparse(result["url"]).hostname
        if domain not in times:
            times[domain] = []
        times[domain].append(result["time_taken"])

    print("Time taken for each domain:")
    for domain, domain_times in times.items():
        print(f"{domain}: {sum(domain_times):.2f} seconds")


if __name__ == "__main__":
    main()
