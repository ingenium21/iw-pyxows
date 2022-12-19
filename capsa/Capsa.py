from requests import Session, request
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Gauge
from time import sleep


class Capsa:
    """A Class to manage the connection to capsa and grab the things we need from their API"""
    
    def __init__(self, url, username, password, logPath, clientId, clientSecret, apiUrl, organizationId, facilityId, cartId, ipAddress):
        """initialization method for the scraper"""
        self.url = url
        self.username = username
        self.password = password
        self.logPath = logPath
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.apiUrl = apiUrl
        self.token = ""
        self.session = Session()
        self.organizationId = organizationId
        self.FacilityId = facilityId
        self.cartId = cartId
        self.cartInfo = {}
        self.ipAddress = ipAddress

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
        endDate = datetime.utcnow()
        startDate = datetime.utcnow() - timedelta(hours=1)
        startDate = datetime.strftime(startDate, "%Y-%m-%dT%H:%M:%S.%f")
        endDate = datetime.strftime(endDate, "%Y-%m-%dT%H:%M:%S.%f")
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
            'StartDateUtc': startDate,
            'EndDateUtc': endDate,
            'LocalMinutesOffset': -360
        }
        #Had to use request because session was sending the wrong auth header
        response = request('POST',response_url, json=payload, headers=self.session.headers)
        if response.status_code == 200:
            voltage = json.loads(response.text)
            #Hiearcahy of the response text is as below.
            voltage = round(voltage['Entities'][0]['Values'][-1]['Value'],2)
            print("getting latest voltage")
            return voltage


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
            self.cartInfo['lastStatusCode'] = 200
            result = json.loads(response.text)
            result = result['Result']
            self.cartInfo['SerialNumber'] = result['SerialNumber']
            self.cartInfo['LastNetworkAccessPoint'] = result['LastKnownNetworkAccessPoint']['Name']
            #converting UTC to EST
            lastConnected = datetime.strptime(result['LastImAliveUtc'],"%Y-%m-%dT%H:%M:%S.%f")
            lastConnected = lastConnected - timedelta(hours=5)
            lastConnected = datetime.strftime(lastConnected,"%Y-%m-%dT%H:%M:%S.%f" )
            self.cartInfo['LastConnected'] = lastConnected
            print(self.cartInfo)
            return(self.cartInfo)
        else:
            self.cartInfo['lastStatusCode'] = response.status_code
            return(self.cartInfo)

        #     return(200)
        # else:
        #     return(400)

    def disconnect_session(self):
        self.session.close()

    def create_gauge_for_metric(self, metric_dict):
        """Creates the gauge metric"""
        metric_name = "cart_battery_voltage{cartName='capsaCart'}"
        
    def set_value(self, metric_dict, value):
        """sets gauge with value"""
    
    def check_log_path(self):
        """Checks to make sure the logpath exists"""
        isExist = os.path.exists(self.logPath)
        if isExist == False:
            os.makedirs(self.logPath)
            
    def append_to_log(self, output, command):
        """This function is primarily used to append the output to the log file"""
        edited_ip = self.ipAddress.replace(".", "_")
        filename = f"{self.logPath}\\{edited_ip}_{command}.json"
        if os.path.exists(filename):
            with open(filename, 'a', encoding='utf-8') as fn:
                json.dump(output, fn)
                fn.write('\n')
        else:
            with open(filename, 'a', encoding='utf-8') as fn:
                json.dump(output, fn)
                fn.write('\n')

    

if __name__ == "__main__":
    start_http_server(9091)
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
    logPath = os.getenv('LOG_PATH')
    ip_address = os.getenv('CE_HOST')

    c = Capsa(url=url, username=username, password=password, logPath=logPath, clientId=clientId, clientSecret=clientSecret, apiUrl=apiUrl, organizationId=organizationId, facilityId=facilityId, cartId=cartId, ipAddress=ip_address)
    c.check_log_path()
    c.create_session()
    c.get_auth_token()
    metric_dict = {}
    metric_name = "cart_battery_voltage"
    metric_dict[metric_name] = Gauge(metric_name, "capsa cart's battery life")


    statusCode = 200
    while statusCode == 200:
        cartInfo = c.get_by_id()
        statusCode = cartInfo['lastStatusCode']
        c.append_to_log(cartInfo,"CapsaCartInfo")
        volt = c.get_battery_voltage()
        metric_dict[metric_name].set(volt)
        sleep(60)
    c.disconnect_session()