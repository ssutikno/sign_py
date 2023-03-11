import http.server
import socketserver
import urllib.parse
import os
import json

PORT = 8000
UPLOAD_DIR = "uploads"

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the homepage
        if self.path == "/":
            response = """
            <!doctype html>
            <html>
            <head><title>Python Web Server Example</title></head>
            <body>
            <h1>Welcome to the Python Web Server Example</h1>
            <p>This is an example of a Python web server that allows you to upload and download files.</p>
            <h2>Upload a File:</h2>
            <form method="get" action="/upload">
            <label>Filename: <input type="text" name="filename"></label>
            <input type="file" name="file">
            <input type="submit" value="Upload">
            </form>
            <br>
            <h2>View Uploaded Files:</h2>
            <p>Click the button below to view a list of uploaded files:</p>
            <form method="get" action="/files">
            <button type="submit">View Files</button>
            </form>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(response, "utf8"))

        # Serve a list of uploaded files as JSON
        elif self.path == "/files":
            file_list = os.listdir(UPLOAD_DIR)
            response = {"files": file_list}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf8"))

        # Stream a requested file
        elif self.path.startswith("/download"):
            # Parse the query string to get the filename
            query = urllib.parse.urlparse(self.path).query
            filename = urllib.parse.parse_qs(query).get("filename", [""])[0]

            # If no filename was provided, return an error response
            if not filename:
                self.send_error(400, "Bad Request: filename parameter missing")
                return

            # Check if the file exists
            file_path = os.path.join(UPLOAD_DIR, filename)
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return

            # Stream the file as the response
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
            self.send_header("Content-Length", os.path.getsize(file_path))
            self.end_headers()
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    self.wfile.write(data)

        # Handle file uploads
        elif self.path.startswith("/upload"):
            # Parse the query string to get the filename
            query = urllib.parse.urlparse(self.path).query
            filename = urllib.parse.parse_qs(query).get("filename", [""])[0]

            # If no filename was provided, return an error response
            if not filename:
                self.send_error(400, "Bad Request: filename parameter missing")
                return

            # Get the file data from the request body
            try:
                length = int(self.headers.get("Content-Length"))
