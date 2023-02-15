import json
import urllib.request as urllib2

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)



def file_get_contents(url):
    url = str(url).replace(" ", "+") # just in case, no space in url
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8'}
    req = urllib2.Request(url, headers=hdr)
    req.add_header('Cache-Control', 'no-cache')
    req.add_header('Pragma', 'no-cache')
    try:
        page = urllib2.urlopen(req)
        return page.read()
    except urllib2.HTTPError as e:
        print(e.fp.read())
    return ''

def file_local_get_contents(uri):
    with open(uri, "r") as fp:
        return fp.read()