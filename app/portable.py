import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Rotating browser-like headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def add_base_tag(html_content, original_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_url = urlparse(original_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    if parsed_url.path and not parsed_url.path.endswith('/'):
        base_url = urljoin(base_url, parsed_url.path.rsplit('/', 1)[0] + '/')

    if not soup.find('base'):
        base_tag = soup.new_tag('base', href=base_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            head_tag = soup.new_tag('head')
            head_tag.insert(0, base_tag)
            soup.insert(0, head_tag)

    return str(soup)

def bypass_paywall(url, retries=3):
    """
    Fetches a webpage with browser-like headers, retries, and safe fallbacks.
    """
    if not url.startswith("http"):
        url = "https://" + url

    for attempt in range(retries):
        try:
            # Optional delay to avoid bot detection
            time.sleep(random.uniform(0.5, 1.2))

            response = requests.get(
                url,
                headers=get_headers(),
                timeout=10,
                allow_redirects=True
            )

            response.raise_for_status()
            response.encoding = response.apparent_encoding

            return add_base_tag(response.text, response.url)

        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                return "Unable to fetch the page after multiple attempts."
            time.sleep(1)

    return "Unexpected error."
