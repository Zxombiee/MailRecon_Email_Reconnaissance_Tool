"""Web Crawler - PLACEHOLDER. Member 2 replaces this file.

Interface that mailrecon.py calls (keep the same name and arguments):

    crawl(start_url, fetcher, max_pages)  ->  yields (page_url, html_text)

    - Use ONLY fetcher.get(url) for every request (including robots.txt).
      It checks the scope and rate limit for you, and raises OutOfScope
      for a host outside scope.txt. Use fetcher.allowed(url) to skip
      out-of-scope links before trying them.
    - Read robots.txt first and skip disallowed paths.
    - Stop after max_pages pages.
    - yield each page as soon as it is fetched (do not collect a list first),
      so the kill switch keeps partial results.

This placeholder only fetches the start page.
"""


def crawl(start_url, fetcher, max_pages):
    response = fetcher.get(start_url)
    yield start_url, response.text
