from scrape import scrape_url
from urllib.parse import urljoin


blacklist = []


def parse_links(url, SITE_DATA, SITE_LINKS, LINKS_FOUND, HISTORY, task_queue, depth=1):
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

        print(f"Found {len(links)} links ({removed} duplicates)\n")
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
        print(f"Found 0 links\n")
