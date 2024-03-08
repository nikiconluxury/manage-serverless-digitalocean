import os
import random
import json
import zlib
import base64
import urllib.request as request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from html.parser import HTMLParser


def fetch_desktop_user_agent(url):
    try:
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            desktop_user_agents = data.get("UserAgents", {}).get("Desktop", [])
            return random.choice(desktop_user_agents) if desktop_user_agents else None
    except URLError as e:
        print(f"Failed to fetch user agents: {e}")
        return None

class UnifiedContentExtractor(HTMLParser):
    def __init__(self, debug=False):
        super().__init__()
        self.recording = 0
        self.data = []
        self.debug = debug

    def handle_starttag(self, tag, attrs):
        if self.debug:
            print(f"Encountered start tag: {tag}")
        # Rest of the code remains the same
        if tag == 'script':
            self.recording = 1
        elif tag == 'table':
            self.recording = 2

    def handle_endtag(self, tag):
        if tag == 'script' and self.recording == 1:
            self.recording = 0
        elif tag == 'table' and self.recording == 2:
            self.recording = 0

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)

    def get_content(self, include_script=True):
        return "".join(self.data) if include_script else ""
def fetch_public_ip():
    try:
        url = 'https://api.ipify.org?format=json'
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("ip")
    except URLError as e:
        print(f"Failed to fetch public IP: {e}")
        return None
def fetch_with_proxy(query):
    user_agent = fetch_desktop_user_agent(os.environ.get('HEADERSURL')) or 'Mozilla/5.0'
    params = urlencode({'q': query, 'tbm': 'isch', 'filter': '0', 'num': '10'})
    full_url = f'https://www.google.com/search?{params}'

    try:
        print(f"Public IP: {fetch_public_ip()}")
        req = request.Request(full_url, headers={'User-Agent': user_agent})
        with request.urlopen(req) as response:
            content = response.read()
            parser = UnifiedContentExtractor(debug=True)
            parser.feed(content.decode('utf-8'))
            extracted_content = ''.join(parser.data).encode('utf-8')
            # Directly compress and encode content
            compressed_content = zlib.compress(extracted_content)
            encoded_content = base64.b64encode(compressed_content).decode('utf-8')
            
            return encoded_content
    except HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except URLError as e:
        print(f"URL error occurred: {e}")
        return None

def main(event):
    query = event.get('query', None)
    if not query:
        return {"statusCode": 400, "body": json.dumps({"message": "No query found in request"})}

    result = fetch_with_proxy(query)
    return {"statusCode": 200, "body": json.dumps({"body": result})}
