"""Tests for the safety controls. Run with: python -m unittest discover tests"""

import unittest

from mailrecon import http, safety


class ScopeTests(unittest.TestCase):
    scope = ["localhost", "127.0.0.1", "192.168.56.0/24", "*.lab.local", "example.com"]

    def test_exact_domain(self):
        self.assertTrue(safety.in_scope("example.com", self.scope))

    def test_ip_in_range(self):
        self.assertTrue(safety.in_scope("192.168.56.20", self.scope))

    def test_ip_outside_range(self):
        self.assertFalse(safety.in_scope("192.168.57.20", self.scope))

    def test_wildcard_subdomain(self):
        self.assertTrue(safety.in_scope("hr.lab.local", self.scope))

    def test_lookalike_domain_refused(self):
        self.assertFalse(safety.in_scope("evil-lab.local.com", self.scope))
        self.assertFalse(safety.in_scope("notexample.com", self.scope))

    def test_subdomain_not_allowed_without_wildcard(self):
        self.assertFalse(safety.in_scope("mail.example.com", self.scope))

    def test_empty_host_refused(self):
        self.assertFalse(safety.in_scope(None, self.scope))

    def test_missing_scope_file_uses_safe_hosts(self):
        self.assertEqual(safety.load_scope("does_not_exist.txt"), sorted(safety.SAFE_HOSTS))


class FetcherTests(unittest.TestCase):
    """The fetcher must refuse out-of-scope URLs before any network connection."""

    def setUp(self):
        self.fetcher = http.Fetcher(["127.0.0.1"], safety.RateLimiter(1), 5, max_requests=5)

    def test_out_of_scope_url_blocked(self):
        with self.assertRaises(safety.OutOfScope):
            self.fetcher.get("https://google.com/")
        self.assertEqual(self.fetcher.blocked, ["https://google.com/"])

    def test_non_http_scheme_blocked(self):
        self.assertFalse(self.fetcher.allowed("ftp://127.0.0.1/"))
        self.assertFalse(self.fetcher.allowed("mailto:ali@127.0.0.1"))

    def test_request_limit(self):
        self.fetcher.limiter.count = 5
        with self.assertRaises(safety.OutOfScope):
            self.fetcher.get("http://127.0.0.1/")


class ConfirmationTests(unittest.TestCase):
    def test_disclaimer_needs_exact_words(self):
        self.assertTrue(safety.show_disclaimer(ask=lambda _: "i agree"))
        self.assertFalse(safety.show_disclaimer(ask=lambda _: "yes"))

    def test_no_input_means_no(self):
        def no_keyboard(_):
            raise EOFError
        self.assertFalse(safety.show_disclaimer(ask=no_keyboard))

    def test_remote_target_must_be_retyped(self):
        self.assertTrue(safety.confirm_remote_target("example.com", ask=lambda _: ""))
        self.assertTrue(safety.confirm_remote_target("hr.lab.local", ask=lambda _: "hr.lab.local"))
        self.assertFalse(safety.confirm_remote_target("hr.lab.local", ask=lambda _: "other"))


class RateLimiterTests(unittest.TestCase):
    def test_delay_cannot_go_below_minimum(self):
        self.assertEqual(safety.RateLimiter(0).delay, safety.MIN_DELAY)


if __name__ == "__main__":
    unittest.main()
