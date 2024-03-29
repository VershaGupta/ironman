#!/usr/bin/python
#################################################
# Class for Initilizing the IronMan Class   #
#################################################
# This is the main class to communicate with    #
# IronMan' Unified User Registration API.
#                                               #
# Please note that some API calls are for       #
# premium or enterprise members only.           #
# In which case, an exception will be raised.   #
#################################################
# Copyright 2019 IronMan.               #                        #
#################################################
# This file is part of the IronMan SDK      #
# package.                                      #
#################################################

__author__ = "IronMan"
__copyright__ = "Copyright 2019, IronMan"
__email__ = "vgversha@gmail.com"
__status__ = "Production"
__version__ = "10.0.1"

import json
import sys
import urllib3
import hmac
import hashlib
import base64
from collections import namedtuple
from datetime import datetime, timedelta
from importlib import import_module

import binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from pbkdf2 import PBKDF2

# Authentication APIs
from IronMan.api.authentication.api import AuthenticationApi

# exception
from IronMan.exceptions import Exceptions

class IronMan:
    """
    IronMan Class. Use this to obtain social data and other information
    from the IronMan API. Requires Python 2.7 or greater.
    """

    API_KEY = None
    LIBRARY = None
    CUSTOM_DOMAIN = None
    API_REQUEST_SIGNING = False
    SERVER_REGION = None
    CONST_INITVECTOR = "tu89geji340t89u2"
    CONST_KEYSIZE = 256

    def __init__(self):
        """
        Constructed when you want to retrieve social data with respect to the acquired token.
        :raise Exceptions.NoAPIKey: Raised if you did not set an API_KEY.
        """
		
        self.error = {}
        self.sociallogin_raw = False
        self.bs = 16
        
        if not self.API_KEY:
            raise Exceptions.NoAPIKey

        self.SECURE_API_URL = "https://api.loginradius.io/"


        # proxy server detail
        self.IS_PROXY_ENABLE = False
        self.USER_NAME = "your-username"
        self.PASSWORD = "your-password"
        self.HOST = "host-name"
        self.PORT = "port"

        # Namedtuple for settings for each request and the api functions.
        self.settings = namedtuple(
            "Settings", ['library', 'urllib', 'urllib2', 'json', 'requests'])

        # We prefer to use requests with the updated urllib3 module.
        try:
            from distutils.version import StrictVersion
            import requests

            if StrictVersion(requests.__version__) < StrictVersion("2.0"):
                raise Exceptions.RequestsLibraryDated(requests.__version__)
            else:
                self._settings("requests")

        # However, we can use urllib if there is no requests or it is outdated.
        except (ImportError, Exceptions.RequestsLibraryDated):
            self._settings("urllib2")

        self.authentication = AuthenticationApi(self)
      
        if sys.version_info[0] < 3:
            from urllib import quote
            self.quote = quote
        else:
            from urllib.parse import quote
            self.quote = quote

    #
    # Internal private functions
    #
    def _settings(self, library):
        """This sets the name tuple settings to whatever library you want.
        You may change this as you wish."""
        if IronMan.LIBRARY is not None:
            if IronMan.LIBRARY == "requests":
                self._set_requests()
            elif IronMan.LIBRARY == "urllib2":
                self._set_urllib2()
            else:
                raise Exceptions.InvalidLibrary(IronMan.LIBRARY)
        else:
            if library == "requests":
                self._set_requests()
            elif library == "urllib2":
                self._set_urllib2()
            else:
                raise Exceptions.InvalidLibrary(library)

    def _set_requests(self):
        """Change to the requests library to use."""
        self.settings.library = "requests"
        self.settings.requests = import_module("requests")
        self.settings.urllib2 = False

    def _set_urllib2(self):
        """Change to the requests urllib2 library to use."""
        if sys.version_info[0] == 2:
            self.settings.urllib2 = import_module("urllib2")
            self.settings.urllib = import_module("urllib")
        else:
            self.settings.urllib2 = import_module("urllib.request")
            self.settings.urllib = import_module("urllib.parse")
        self.settings.library = "urllib2"
        self.settings.requests = False
        self.settings.json = import_module("json")

    def get_expiry_time(self):
        utc_time = datetime.utcnow()
        expiry_time = utc_time + timedelta(hours=1)
        return expiry_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_digest(self, expiry_time, url, payload=None):
        encoded_url = self.quote(url.lower(), safe='')
        signing_str = expiry_time + ":" + encoded_url
        signing_str = signing_str.lower()
        if payload is not None:
            signing_str = signing_str + ":" + json.dumps(payload)

        key_bytes = self.get_api_secret()
        data_bytes = signing_str
        if sys.version_info[0] >= 3:
            key_bytes = bytes(self.get_api_secret(), 'latin-1')
            data_bytes = bytes(signing_str, 'latin-1')
        dig = hmac.new(key_bytes, msg=data_bytes, digestmod=hashlib.sha256).digest()
        if sys.version_info[0] >= 3:
            return base64.b64encode(dig).decode("utf-8")
        return base64.b64encode(dig)

    def execute(self, method, resource_url, query_params, payload):
        api_end_point = self.SECURE_API_URL + resource_url

        
        if self.SERVER_REGION is not None and self.SERVER_REGION != "":
            query_params['region'] = self.SERVER_REGION

        apiSecret = None
        if "apiSecret" in query_params:
            apiSecret = query_params['apiSecret']
            query_params.pop("apiSecret")

        headers = {'Content-Type': "application/json",
                   'Accept-encoding': 'gzip'}

        if "access_token" in query_params and "/auth" in resource_url:
            headers.update({"Authorization": "Bearer " + query_params['access_token']})
            query_params.pop("access_token")


        if apiSecret and "/manage" in resource_url and not self.API_REQUEST_SIGNING:
            headers.update({"X-IronMan-ApiSecret": apiSecret})

        api_end_point = api_end_point + "?"
        for key, value in query_params.items():
            api_end_point = api_end_point + key + "=" + str(value) + "&"

        api_end_point = api_end_point[:-1]

        if apiSecret and "/manage" in resource_url and self.API_REQUEST_SIGNING:
            expiry_time = self.get_expiry_time()
            digest = self.get_digest(expiry_time, api_end_point, payload)
            headers.update({"X-Request-Expires": expiry_time})
            headers.update({"digest": "SHA-256=" + digest})

        try:
            if method.upper() == 'GET':
                return self._get_json(api_end_point, {}, headers)
            else:
                return self.__submit_json(method.upper(), api_end_point, payload, headers)
        except IOError as e:
            return {
                'ErrorCode': 105,
                'Description': e.message
            }
        except ValueError as e:
            return {
                'ErrorCode': 102,
                'Description': e.message
            }
        except Exception as e:
            return {
                'ErrorCode': 101,
                'Description': e.message
            }

    def _get_json(self, url, payload, HEADERS):
        """Get JSON from IronMan"""

        proxies = self._get_proxy()

        if self.settings.requests:
            r = self.settings.requests.get(
                url, proxies=proxies, params=payload, headers=HEADERS)
            return self._process_result(r.json())
        else:
            http = urllib3.PoolManager()
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            r = http.request('GET', url, fields=payload, headers=HEADERS)
            return json.loads(r.data.decode('utf-8'))

    def __submit_json(self, method, url, payload, HEADERS):
        if self.settings.requests:
            import json
            proxies = self._get_proxy()
            if method == 'PUT':
                r = self.settings.requests.put(
                    url, proxies=proxies, data=json.dumps(payload), headers=HEADERS)
            elif method == 'DELETE':
                r = self.settings.requests.delete(
                    url, proxies=proxies, data=json.dumps(payload), headers=HEADERS)
            else:
                r = self.settings.requests.post(
                    url, proxies=proxies, data=json.dumps(payload), headers=HEADERS)
            return self._process_result(r.json())

        else:
            import json
            data = json.dumps(payload)
            if sys.version_info[0] == 3:
                data = data.encode('utf-8')

            r = self.settings.urllib2.Request(
                url, data, {'Content-Type': 'application/json', 'Accept-encoding': 'gzip'})
            if method == 'PUT' or method == 'DELETE':
                r.get_method = lambda: method
            for key, value in HEADERS.items():
                r.add_header(key, value)
            try:
                result = self.settings.urllib2.urlopen(r)
            except self.settings.urllib2.HTTPError as e:
                return json.loads(e.read())

            import codecs
            reader = codecs.getreader("utf-8")
            return self._process_result(self.settings.json.load(reader(result)))

    def get_api_key(self):
        return self.API_KEY

    def get_api_secret(self):
        return self.API_SECRET

    def _get_proxy(self):
        if self.IS_PROXY_ENABLE:
            proxies = {'https': 'https://' + self.USER_NAME + ':' + self.PASSWORD + '@' + self.HOST + ':' + self.PORT}
        else:
            proxies = {}
        return proxies

    def _process_result(self, result):
        # For now, directly returning the API response
        return result

    #
    # Public functions
    #
    def change_library(self, library):
        self._settings(library)

    def is_null_or_whitespace(self, value):
        if value is None:
            return True
        if str(value).strip() == "":
            return True

    def get_validation_message(self, field):
        return "Invalid value for field " + str(field)
    
    def get_sott(self, time='10', getLRserverTime=False):
        if getLRserverTime:
            result = self.configuration.get_server_info()
            print(result)
            if result.get('Sott') is not None:
                Sott = result.get('Sott')
                for timeKey, val in Sott.items():
                    if timeKey == 'StartTime':
                        now = val
                    if timeKey == 'EndTime':
                        now_plus_10m = val
            else:
                now = datetime.utcnow()
                now = now - timedelta(minutes=5)
                now_plus_10m = now + timedelta(minutes=10)
                now = now.strftime("%Y/%m/%d %I:%M:%S")
                now_plus_10m = now_plus_10m.strftime("%Y/%m/%d %I:%M:%S")

        else:
            now = datetime.utcnow()
            now = now - timedelta(minutes=5)
            now_plus_10m = now + timedelta(minutes=10)
            now = now.strftime("%Y/%m/%d %I:%M:%S")
            now_plus_10m = now_plus_10m.strftime("%Y/%m/%d %I:%M:%S")

        plaintext = now + "#" + self.API_KEY + "#" + now_plus_10m
        padding = 16 - (len(plaintext) % 16)
        if sys.version_info[0] == 3:
            plaintext += (bytes([padding]) * padding).decode()
        else:
            plaintext += (chr(padding) * padding).decode()

        salt = "\0\0\0\0\0\0\0\0"
        cipher_key = PBKDF2(self.API_SECRET,
                            salt, 10000).read(self.CONST_KEYSIZE // 8)

        if sys.version_info[0] == 3:
            iv = bytes(self.CONST_INITVECTOR, 'utf-8')
            text = bytes(plaintext, 'utf-8')
        else:
            iv = str(self.CONST_INITVECTOR)
            text = str(plaintext)

        backend = default_backend()
        cipher = Cipher(algorithms.AES(cipher_key),
                        modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(text) + encryptor.finalize()

        base64cipher = base64.b64encode(ct)

        md5 = hashlib.md5()
        md5.update(base64cipher.decode('utf8').encode('ascii'))
        return base64cipher.decode('utf-8')+"*"+binascii.hexlify(md5.digest()).decode('ascii')
