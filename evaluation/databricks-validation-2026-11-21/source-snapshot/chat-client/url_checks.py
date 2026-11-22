"""Bounded HTTP(S) citation scanner for evaluation, not a claim-support grader.

Recognizes URL boundaries in inline Markdown, autolinks and plain text. Balanced
parentheses and Markdown-escaped parentheses remain in destinations. This is not
a complete CommonMark renderer. See https://spec.commonmark.org/0.31.2/#links .
"""
import html
import re


def extract_urls(text):
    text = html.unescape(text)
    found = []
    for match in re.finditer(r'https?://', text):
        i = match.start()
        depth = 0
        chars = []
        while i < len(text):
            char = text[i]
            if char.isspace() or char in '<>"\'`[]':
                break
            if char == '\\':
                if i + 1 < len(text) and text[i + 1] in '()':
                    chars.append(text[i + 1]); i += 2; continue
                break
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            chars.append(char); i += 1
        url = ''.join(chars).rstrip('.,;:')
        if url not in {'http://', 'https://'}:
            found.append(url)
    return found


def normalize_url(url):
    # Preserve the preceding checker's comparison semantics. Do not equate
    # distinct query strings, decode reserved characters or resolve redirects.
    return html.unescape(url).rstrip('/')


def check_url_membership(answer, source_texts):
    sources = {normalize_url(u) for text in source_texts for u in extract_urls(text)}
    answer_urls = [normalize_url(u) for u in extract_urls(answer)]
    unmatched = [u for u in answer_urls if u not in sources]
    return {'answer_urls':answer_urls, 'unmatched_urls':unmatched,
            'citation_provenance':bool(answer_urls) and not unmatched}
