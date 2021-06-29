from http.server import BaseHTTPRequestHandler
import json
from api.fetch_kickstarter.scripts import fetch_kickstarter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        res = fetch_kickstarter()

        self.wfile.write(res.encode())

        return