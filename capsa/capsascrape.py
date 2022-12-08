from requests import Session
import json
from bs4 import BeautifulSoup

class Capsascrape:
    """A Class to manage the connection to capsa and grab the things we need from their API"""
    
    def __init__(self, url, username, password):
        """initialization method for the scraper"""
        self.url = url
        self.username = username
        self.password = password

    def create_session(self):
        """Creates a session using the python requests library.
        Takes in the url to login, username, and password.
        Returns the session.
        """
        s = Session()
        s.auth = (self.username,self.password)
        #s.headers.update({'Accept': 'application/json'})
        
        payload = {
            "username": self.username,
            "password": self.password
        }

        #setting the response url to the page you want to acces after logging in
        response_url = "https://nsight2.capsahealthcare.com/dashboard"

        response = s.get(response_url)

        if response.url == response_url:
            print("login successful")
            print("trying api")
            response = s.post("https://capsa-api.capsahealthcare.com/api/auth/getauth")
            soup = BeautifulSoup(response.text, "html.parser")
            print(soup.prettify())

        else:
            print("login failed!")



if __name__ == "__main__":
    url = "https://nsight2.capsahealthcare.com/"
    username = "r_regalado"
    password = "CEFr5^Ji8&HgtY"
    c = Capsascrape(url=url, username=username, password=password)
    c.create_session()