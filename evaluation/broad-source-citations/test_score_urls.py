import unittest
from score import normalize_url

class CitationParsingTests(unittest.TestCase):
    def test_square_bracket(self):
        self.assertEqual(normalize_url('https://clinicaltrials.gov/study/NCT00000000]'), 'https://clinicaltrials.gov/study/NCT00000000')
    def test_markdown_parenthesis(self):
        self.assertEqual(normalize_url('https://example.org/a_(b)).'), 'https://example.org/a_(b)')
    def test_different_revision_stays_different(self):
        self.assertNotEqual(normalize_url('https://example.org/abc123/file.csv'), normalize_url('https://example.org/abc124/file.csv'))
    def test_query_preserved(self):
        self.assertEqual(normalize_url('https://example.org/?a=1&amp;b=2'), 'https://example.org/?a=1&b=2')

if __name__ == '__main__': unittest.main()
