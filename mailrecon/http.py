"""Shared HTTP client (Member 1).

Every web request in MailRecon MUST go through Fetcher.get(). It enforces:
  - the scope: a URL whose host is not in scope.txt is refused BEFORE any connection
  - the rate limit: waits between requests
  - no automatic redirects: a redirect is returned, and the crawler must
    call get() again for the new URL, so the scope check runs again
  - a page limit: stops after max_requests, even if the crawler has a bug
"""

from urllib.parse import urlparse

import requests

from . import safety

USER_AGENT = "MailRecon/1.0 (authorised security assessment)"


class Fetcher:
    def __init__(self, scope, limiter, timeout, max_requests):
        self.scope = scope
        self.limiter = limiter
        self.timeout = timeout
        self.max_requests = max_requests
        self.blocked = []        # out-of-scope URLs that were refused

    def allowed(self, url):
        """True if the URL is http/https and its host is in scope."""
        parts = urlparse(url)
        return parts.scheme in ("http", "https") and safety.in_scope(parts.hostname, self.scope)

    def get(self, url):
        """Fetch one URL. Raises OutOfScope if the host is not authorised."""
        if not self.allowed(url):
            self.blocked.append(url)
            raise safety.OutOfScope(url)
        if self.limiter.count >= self.max_requests:
            raise safety.OutOfScope(f"request limit of {self.max_requests} reached")
        self.limiter.wait()
        return requests.get(url, headers={"User-Agent": USER_AGENT},
                            timeout=self.timeout, allow_redirects=False)
