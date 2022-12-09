from requests import Session
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

class Capsascrape:
    """A Class to manage the connection to capsa and grab the things we need from their API"""
    
    def __init__(self, url, username, password, clientId, clientSecret, apiUrl):
        """initialization method for the scraper"""
        self.url = url
        self.username = username
        self.password = password
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.apiUrl = apiUrl
        self.token = ""
        self.session = Session()

    def create_session(self):
        """Creates a session using the python requests library.
        Takes in the url to login, username, and password.
        Returns the session.
        """
        self.session.auth = (self.username,self.password)

        #setting the response url to the page you want to acces after logging in
        response_url = f"{self.url}/dashboard"

        response = self.session.get(response_url)

        if response.url == response_url:
            print("login successful")
        else:
            print("login failed!")

    def get_auth_token(self):
        authUrl = f"{self.apiUrl}/auth/getauth"
        response = self.session.options(authUrl)
        if response.status_code == 200:
            print("options response 200")
            payload = {"password":self.password,"userName":self.username,"clientId":self.clientId,"clientSecret":self.clientSecret}
            response = self.session.post(authUrl, data=payload)
            if response.status_code == 200:
                print("post response 200")
                token = json.loads(response.text)
                token = token['Result']['Token']
                self.token = token

    def disconnect_session(self):
        self.session.close()


if __name__ == "__main__":
    load_dotenv()
    url = os.getenv('CAP_URL')
    apiUrl = os.getenv('CAP_API_URL')
    username = os.getenv('CAP_USER')
    password = os.getenv('CAP_PASS')
    clientId = os.getenv('CAP_CLIENT_ID')
    clientSecret = os.getenv('CAP_CLIENT_SECRET')
    c = Capsascrape(url=url, username=username, password=password, clientId=clientId, clientSecret=clientSecret, apiUrl=apiUrl)
    c.create_session()
    c.get_auth_token()
    c.disconnect_session()