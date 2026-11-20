
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestWebsite(BaseHTTPRequestHandler):

    def do_GET(self):
        pages = {
            "/": """
                <html>
                <h1>MailRecon Test Website</h1>
                <p>Welcome to our fake company website.</p>
                <p>Contact: john.smith@testcompany.local</p>
                <a href="/about">About Us</a>
                <a href="/contact">Contact</a>
                </html>
            """,

            "/about": """
                <html>
                <h1>About Us</h1>
                <p>Email: jane.doe@testcompany.local</p>
                <p>Email: ali.ahmad@testcompany.local</p>
                <a href="/">Home</a>
                </html>
            """,

            "/contact": """
                <html>
                <h1>Contact Us</h1>
                <p>Email: michael.lee@testcompany.local</p>
                <p>Email: support@testcompany.local</p>
                <a href="/">Home</a>
                </html>
            """
        }

        path = self.path.split("?")[0]
        content = pages.get(path)

        if content is None:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8080), TestWebsite)

    print("MailRecon test website is running!")
    print("Open http://127.0.0.1:8080 in your browser")

    server.serve_forever()
