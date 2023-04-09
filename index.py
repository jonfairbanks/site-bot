import json, requests, sys, time

from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

from file import save_json
from graphs import generate_history_graph, generate_waterfall
from scrape import scrape_url


SITE_DATA = {}
SITE_LINKS = {}
LINKS_FOUND = 0
HISTORY = []


session = requests.Session()
task_queue = Queue()

url_scrape_list = sys.argv[1].split(",")
blacklist = []


def worker(queue):
    while not queue.empty():
        task = queue.get()
        parse_links(*task)
        queue.task_done()


def parse_links(url, depth=1):
    global LINKS_FOUND
    if depth > 3:
        return

    if url not in SITE_DATA:
        SITE_DATA[url] = []

    if url not in SITE_LINKS:
        SITE_LINKS[url] = []

    print(f"Scraping: {url}")
    data = scrape_url(url, HISTORY)

    if data is not None:
        # Save a copy of all site HTML
        SITE_DATA[url].append(str(data))
        SITE_DATA[url].sort()

        # Extract links
        links = data.find_all("a", href=True)
        before = len(links)

        # Remove duplicate links
        links = list(dict.fromkeys(links))
        after = len(links)

        removed = before - after

        print(f"Found {len(links)} unique links ({removed} duplicates)\n")
        LINKS_FOUND += len(links)

        for link in links:
            # Create links and save a copy
            absolute_link = urljoin(url, link["href"])
            if absolute_link not in SITE_LINKS[url]:
                SITE_LINKS[url].append(absolute_link)
                SITE_LINKS[url].sort()

            # Recursively call parse_links() with increased depth
            if absolute_link not in blacklist:
                task_queue.put((absolute_link, depth + 1))
    else:
        print(f"Found 0 links (0 duplicates)\n")


def main():
    # Start timer
    start_time = time.time()

    # Run app
    with ThreadPoolExecutor(max_workers=5) as executor:
        for start_url in url_scrape_list:
            task_queue.put((start_url, 1))
        futures = [executor.submit(worker, task_queue) for _ in range(5)]
        for f in as_completed(futures):
            pass

    # Save scraped results to JSON
    save_json(SITE_DATA, "SITE_DATA")
    save_json(SITE_LINKS, "SITE_LINKS")

    # Save history graph
    generate_history_graph(HISTORY, "HISTORY_GRAPH")

    # Save waterfall diagram
    generate_waterfall(HISTORY, "HISTORY_WATERFALL")

    # Stop timer & print totals
    end_time = time.time()
    elapsed_time = f"{(end_time - start_time):.2f}"
    print(f"\nCrawled {LINKS_FOUND:,d} links in {elapsed_time}s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)
