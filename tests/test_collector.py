# test extractor.py n crawler.py
# Run: python -m unittest discover tests

import unittest

from mailrecon import crawler, safety
from mailrecon.extractor import extract_emails


class ExtractorTests(unittest.TestCase):
    def test_plain_email(self):
        self.assertEqual(extract_emails("Contact ali@example.com today"), {"ali@example.com"})

    def test_mailto_link(self):
        self.assertEqual(extract_emails('<a href="mailto:siti@example.com">Email</a>'), {"siti@example.com"})

    def test_obfuscated_email(self):
        text = "chong [at] example [dot] com and raju(at)example(dot)com"
        self.assertEqual(extract_emails(text), {"chong@example.com", "raju@example.com"})

    def test_html_encoded_email(self):
        self.assertEqual(extract_emails("ali&#64;example.com"), {"ali@example.com"})

    def test_image_name_is_not_email(self):
        self.assertEqual(extract_emails('<img src="logo@2x.png">'), set())

    def test_empty_page(self):
        self.assertEqual(extract_emails(""), set())


class FakeResponse:
    def __init__(self, status=200, text="", content_type="text/html", location=None):
        self.status_code = status
        self.text = text
        self.headers = {"Content-Type": content_type, "Location": location or ""}


class FakeFetcher:
    """Pretends to be Member 1's Fetcher, but returns pages from a dictionary."""

    def __init__(self, pages):
        self.pages = pages
        self.blocked = []
        self.requested = []

    def allowed(self, url):
        return url.startswith("http://127.0.0.1:8080/")

    def get(self, url):
        self.requested.append(url)
        return self.pages.get(url, FakeResponse(404))


SITE = "http://127.0.0.1:8080"
FAKE_PAGES = {
    f"{SITE}/robots.txt": FakeResponse(200, "User-agent: *\nDisallow: /private/", "text/plain"),
    f"{SITE}/": FakeResponse(200, '<a href="/team.html">Team</a> <a href="/private/hr.html">HR</a> '
                                  '<a href="https://evil.com/">Other site</a> <a href="/menu.pdf">PDF</a> '
                                  '<a href="/old">Old page</a>'),
    f"{SITE}/team.html": FakeResponse(200, '<a href="/">Home</a> ali@example.com'),
    f"{SITE}/old": FakeResponse(301, location="/contact.html"),
    f"{SITE}/contact.html": FakeResponse(200, "info [at] example [dot] com"),
    f"{SITE}/private/hr.html": FakeResponse(200, "secret@example.com"),
}


class CrawlerTests(unittest.TestCase):
    def run_crawl(self, max_pages=20):
        fetcher = FakeFetcher(FAKE_PAGES)
        pages = dict(crawler.crawl(SITE, fetcher, max_pages))
        return pages, fetcher

    def test_visits_pages_and_follows_redirect(self):
        pages, _ = self.run_crawl()
        self.assertEqual(set(pages), {f"{SITE}/", f"{SITE}/team.html", f"{SITE}/contact.html"})

    def test_obeys_robots_txt(self):
        _, fetcher = self.run_crawl()
        self.assertNotIn(f"{SITE}/private/hr.html", fetcher.requested)

    def test_does_not_visit_other_websites(self):
        _, fetcher = self.run_crawl()
        self.assertIn("https://evil.com/", fetcher.blocked)
        self.assertNotIn("https://evil.com/", fetcher.requested)

    def test_skips_files(self):
        _, fetcher = self.run_crawl()
        self.assertNotIn(f"{SITE}/menu.pdf", fetcher.requested)

    def test_max_pages(self):
        pages, _ = self.run_crawl(max_pages=1)
        self.assertEqual(len(pages), 1)

    def test_request_limit_stops_crawl(self):
        fetcher = LimitedFetcher(FAKE_PAGES)
        pages = dict(crawler.crawl(SITE, fetcher, 20))
        self.assertEqual(list(pages), [f"{SITE}/"])     # robots.txt + 1 page, then stop


class LimitedFetcher(FakeFetcher):
    """A fake fetcher that only allows 2 requests, like Member 1's request limit."""

    def get(self, url):
        if len(self.requested) >= 2:
            raise safety.OutOfScope("request limit of 2 reached")
        return super().get(url)


if __name__ == "__main__":
    unittest.main()
