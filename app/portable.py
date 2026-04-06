import flask
from flask import request
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# ---------------------------------------------------------
# Flask App
# ---------------------------------------------------------
app = flask.Flask(__name__)

# ---------------------------------------------------------
# HTML UI
# ---------------------------------------------------------
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>13ft Ladder</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 40px auto; }
        input[type=text] { width: 100%; padding: 10px; margin-bottom: 10px; }
        input[type=submit] { padding: 10px; width: 100%; background: purple; color: white; border: none; }
    </style>
</head>
<body>
    <h1>Enter Website Link</h1>
    <form action="/article" method="post">
        <input type="text" name="link" placeholder="https://example.com/article" required>
        <input type="submit" value="Fetch Article">
    </form>
</body>
</html>
"""

# ---------------------------------------------------------
# Rotating Headers
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Add <base> tag to fix relative links
# ---------------------------------------------------------
def add_base_tag(html_content, original_url):
    soup = BeautifulSoup(html_content, "html.parser")
    parsed = urlparse(original_url)

    base_url = f"{parsed.scheme}://{parsed.netloc}/"
    if parsed.path and not parsed.path.endswith("/"):
        base_url = urljoin(base_url, parsed.path.rsplit("/", 1)[0] + "/")

    if not soup.find("base"):
        base_tag = soup.new_tag("base", href=base_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            head = soup.new_tag("head")
            head.insert(0, base_tag)
            soup.insert(0, head)

    return str(soup)

# ---------------------------------------------------------
# Fetch Page with Retry + Random Delay
# ---------------------------------------------------------
def bypass_paywall(url, retries=3):
    if not url.startswith("http"):
        url = "https://" + url

    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.4, 1.2))

            response = requests.get(
                url,
                headers=get_headers(),
                timeout=10,
                allow_redirects=True
            )

            response.raise_for_status()
            response.encoding = response.apparent_encoding

            return add_base_tag(response.text, response.url)

        except Exception:
            if attempt == retries - 1:
                return "<h2>Failed to fetch the page after multiple attempts.</h2>"
            time.sleep(1)

    return "<h2>Unexpected error.</h2>"

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.route("/")
def index():
    return HTML_FORM

@app.route("/article", methods=["POST"])
def article_post():
    link = request.form.get("link", "")
    return bypass_paywall(link)

@app.route("/<path:url>")
def article_direct(url):
    full_url = "https://" + url
    return bypass_paywall(full_url)

# ---------------------------------------------------------
# Local Dev Server
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
