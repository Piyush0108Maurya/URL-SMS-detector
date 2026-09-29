import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.normalize import normalize_url

class TestNormalizeUrl(unittest.TestCase):
    def test_https_www_trailing_slash(self):
        self.assertEqual(normalize_url("https://www.GitHub.com/"), "github.com")

    def test_http_no_www(self):
        self.assertEqual(normalize_url("http://example.com"), "example.com")

    def test_whitespace(self):
        self.assertEqual(normalize_url("   https://www.test.com/  "), "test.com")

    def test_bare_domain(self):
        self.assertEqual(normalize_url("bare-domain.net"), "bare-domain.net")

    def test_complex_path(self):
        self.assertEqual(normalize_url("HTTPS://WWW.EXAMPLE.COM/about/us/"), "example.com/about/us")

if __name__ == "__main__":
    unittest.main()
