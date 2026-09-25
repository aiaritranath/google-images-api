import os
import json
import serpapi
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # --- Parse query parameters ---
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # --- Validate private key ---
        provided_key = params.get("key", [None])[0]
        if provided_key != "aritra":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Unauthorized",
                "message": "A valid API key is required. Pass ?key=aritra"
            }).encode())
            return

        # --- Get search query ---
        query = params.get("q", ["flowers"])[0]

        # --- Call SerpApi ---
        try:
            client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
            results = client.search({
                "engine": "google_images",
                "q": query,
                "location": "Austin, Texas, United States",
                "google_domain": "google.com",
                "hl": "en",
                "gl": "us"
            })
            images_results = results.get("images_results", [])
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "SerpApi request failed",
                "detail": str(e)
            }).encode())
            return

        # --- Build final response with developer credit ---
        response = {
            "developer": "@its_aritra_nath",
            "query": query,
            "total_results": len(images_results),
            "images_results": images_results
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())