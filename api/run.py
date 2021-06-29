from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        try:
            response = requests.get("http://localhost:3000/api/fetch_kickstarter/run")
            response.raise_for_status()
        except Exception as e:
            print(e)

        if response.status_code != 200:
            print("Error fetching endpoint")
        else:
            res = response.json()
            result = json.dumps(res)
            self.wfile.write(result.encode())

        return