from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import requests
import webbrowser
import os

# Global variables for client ID, secret, and redirect URI
client_id = os.getenv('CONSUMER_KEY')
client_secret = os.getenv('CONSUMER_SECRET')
redirect_uri = 'https://wildly-innocent-pelican.ngrok-free.app'

# print(client_id)
# print(client_secret)
# print(redirect_uri)

# Step 2: Authorization Request - Direct user to Yahoo's authorization endpoint
def open_authorization_url():
    encoded_redirect_uri = quote(redirect_uri, safe='')
    auth_url = f'https://api.login.yahoo.com/oauth2/request_auth?client_id={client_id}&redirect_uri={encoded_redirect_uri}&response_type=code'
    webbrowser.open(auth_url)

# Step 4: Exchanging the Authorization Code for an Access Token
def exchange_code_for_token(authorization_code):
    token_url = 'https://api.login.yahoo.com/oauth2/get_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        access_token_info = response.json()
        access_token = access_token_info.get('access_token')
        print(f"Access Token: {access_token}")
        # You can now use the access token to make authenticated requests to the Yahoo! API
    else:
        print("Failed to obtain access token")

# Step 3: Handling the Redirect - HTTP server to capture the authorization code
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        authorization_code = query_params.get('code', [None])[0]

        if authorization_code:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization code received. Exchanging for an access token...")
            exchange_code_for_token(authorization_code)  # Exchange the code for a token
        else:
            self.send_error(400, "No authorization code provided.")

if __name__ == '__main__':
    # Start the authorization process
    open_authorization_url()
    
    # Start the HTTP server to listen for the OAuth callback
    server_address = ('localhost', 8080)  # Port 8080 or any port that suits your setup
    httpd = HTTPServer(server_address, OAuthHandler)
    print(f"Starting server on {server_address[0]}:{server_address[1]}")
    httpd.serve_forever()