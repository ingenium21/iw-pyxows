from requests import Session, request
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

class Capsascrape:
    """A Class to manage the connection to capsa and grab the things we need from their API"""
    
    def __init__(self, url, username, password, clientId, clientSecret, apiUrl, organizationId, facilityId, cartId):
        """initialization method for the scraper"""
        self.url = url
        self.username = username
        self.password = password
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.apiUrl = apiUrl
        self.token = ""
        self.session = Session()
        self.organizationId = organizationId
        self.FacilityId = facilityId
        self.cartId = cartId

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
                self.session.headers.update = {
                    'Authorization': 'Bearer ' + self.token,
                    'Content-Type': 'application/json',
                    'User-Agent': 'curl/7.83.1',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,es-MX;q=0.8,es-US;q=0.7,es;q=0.6',
                    'Content-Length': '219',
                    'Connection': 'keep-alive'
                }

    def get_battery_voltage(self):
        """Gets the battery voltage of the cart so far we will be querying a part of the capsa API
        That only grabs this data from a chart, so will require a startTime and endTime.  
        If we can figure out a better API endpoint we can change it to that
        ChartQuery=1 for battery voltage
        time will be in UTC
        """
        response_url = f"{self.apiUrl}/analytics/chart"
        endDate = datetime.utcnow
        startDate = datetime.utcnow() - timedelta(hours=1)
        self.session.headers = {
                    'Authorization': 'Bearer ' + self.token,
                    'Content-Type': 'application/json',
                    'User-Agent': 'curl/7.83.1',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,es-MX;q=0.8,es-US;q=0.7,es;q=0.6',
                    'Connection': 'keep-alive'
                }
        payload = {
            'OrganizationId': self.organizationId,
            'FacilityId': self.FacilityId,
            'DeviceType': 9,
            'ChartQuery': 1,
            'GraphyByEntity': 1,
            'Ids': [
                self.cartId
            ],
            'StartDateUtc': '2022-12-12T06:00:00.000Z',
            'EndDateUtc': '2022-12-13T06:00:00.000Z',
            'LocalMinutesOffset': -360
        }
        #Had to use request because session was sending the wrong auth header
        response = request('POST',response_url, json=payload, headers=self.session.headers)
        if response.status_code == 200:
            voltage = json.loads(response.text)
            #Hiearcahy of the response text is as below.
            voltage = voltage['Entities'][0]['Values'][-1]['Value']
            print("getting latest voltage")
            print(voltage)


    def get_by_id(self):
        """gets all the cart info"""
        self.session.headers = {
                    'Authorization': 'Bearer ' + self.token,
                    'Content-Type': 'application/json',
                    'User-Agent': 'curl/7.83.1',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,es-MX;q=0.8,es-US;q=0.7,es;q=0.6',
                    'Connection': 'keep-alive'
                }
        response_url = f"{self.apiUrl}/cart/GetById"
        payload = {
            'Id': self.cartId
        }
        response = request('POST', response_url, json=payload, headers=self.session.headers)
        if response.status_code == 200:
            text = response.text
            print(text)

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
    organizationId = os.getenv('CAP_ORG_ID')
    organizationId = int(organizationId)
    facilityId = os.getenv('CAP_FACILITY_ID')
    facilityId = int(facilityId)
    cartId = os.getenv('CAP_CART_ID')

    c = Capsascrape(url=url, username=username, password=password, clientId=clientId, clientSecret=clientSecret, apiUrl=apiUrl, organizationId=organizationId, facilityId=facilityId, cartId=cartId)
    c.create_session()
    c.get_auth_token()
    c.get_battery_voltage()
    c.disconnect_session()