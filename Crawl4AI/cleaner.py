import trafilatura
import re
from bs4 import BeautifulSoup

JUNK_PATTERNS = [
    re.compile(r"subscribe", re.IGNORECASE),
    re.compile(r"cookie consent", re.IGNORECASE),
    re.compile(r"related posts", re.IGNORECASE),
    re.compile(r"read more", re.IGNORECASE),
    re.compile(r"privacy policy", re.IGNORECASE),
]


def clean_with_trafilatura(html_content):
    # Fixed: Changed "text" to "txt" which is a supported format
    extracted_text = trafilatura.extract(html_content, output_format="txt")

    if not extracted_text:
        soup = BeautifulSoup(html_content, 'html.parser')
        article_body = soup.find('article')
        extracted_text = article_body.get_text() if article_body else ""

    for pattern in JUNK_PATTERNS:
        extracted_text = pattern.sub("", extracted_text)

    return extracted_text.strip()