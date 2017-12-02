import pycurl
import urllib.parse
from collections import defaultdict
from io import BytesIO
import json

def pycurlgetURL(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return json.loads(body.decode('iso-8859-1'))

def pycurlget(url, params):
    buffer = BytesIO()
    c = pycurl.Curl()
    pairs = urllib.parse.urlencode(params)
    c.setopt(c.URL, url+'?'+pairs)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return json.loads(body.decode('iso-8859-1'))

def pycurlpost(url, params): 
    buffer = BytesIO()
    c = pycurl.Curl()
    pairs = urllib.parse.urlencode(params)
    c.setopt(c.URL, url)
    c.setopt(c.POSTFIELDS, pairs)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return json.loads(body.decode('iso-8859-1'))