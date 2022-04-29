import logging
import requests

from config import SERVER_URL, CLIENT_ID, CLIENT_SECRET

# url about oauth
auth_urls = {
    "auth_base": "https://bgm.tv/oauth/authorize",
    "get_token": "https://bgm.tv/oauth/access_token",
    "refresh_token": "https://bgm.tv/oauth/access_token",
    "token_status": "https://bgm.tv/oauth/token_status"
}

api_base_url = "https://api.bgm.tv"


# create headers for logging or access api services
def generate_headers(logged=False, access_token=None):
    headers = {
        'user-agent': 'bangumi-pusher/0.1',
        'content-type': 'application/x-www-form-urlencoded',
        "accept": "application/json"
    }
    if logged and access_token is not None:
        headers['Authorization'] = 'Bearer ' + access_token
        del headers['content-type']

    return headers


# return oauth url
def build_authorization_url(client_id):
    base_url = auth_urls['auth_base']
    return "{}?client_id={}&response_type=code".format(base_url, client_id)


class Client:
    def __init__(self, client_id, client_secret):
        self.access_token = ""
        self.client_id = client_id
        self.client_secret = client_secret
        self.logger = logging.getLogger(str(self.__class__))

    # exchange code to access_token
    def auth(self, code):
        request_body = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": SERVER_URL
        }
        r = requests.post(
            auth_urls["get_token"],
            data=request_body,
            headers=generate_headers()
        )
        if not r.status_code == 200:
            return "Network Error, code is {}".format(r.status_code)
        content = r.json()
        try:
            self.access_token = content['access_token']
            return "done"
        except KeyError:
            self.logger.error("Cannot auth, error message is {}".format(
                content['error_description']))
            return content['error_description']

    def refresh(self):
        request_body = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.access_token,
            "redirect_uri": SERVER_URL
        }
        r = requests.post(
            auth_urls["refresh_token"],
            data=request_body,
            headers=generate_headers()
        )

        if r.status_code != 200:
            return "Network Error, code is {}".format(r.status_code)

        content = r.json()
        try:
            self.access_token = content['access_token']
            return "done"
        except KeyError:
            self.logger.error("Cannot auth, error message is {}".format(
                content['error_description']))
            return content['error_description']

    def get_token(self):
        return self.access_token


client = Client(CLIENT_ID, CLIENT_SECRET)
