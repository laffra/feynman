import json
import time
import urllib.request
import socket


GEOLOCATION_SERVER = "geolocation-db.com/json"
FAIL = 1000


def getDetails(location):
    return location["country_name"]

def readUrl(url):
    return urllib.request.urlopen(f"https://{url}").read().decode()

def callService(url):
    response = readUrl(url)
    if response.startswith("callback("):
        response = response[9:-1]
    return json.loads(response)

def getMyLocation():
    return getDetails(callService(GEOLOCATION_SERVER))

def getLocation(ip):
    if ip == "127.0.0.1":
        return getMyLocation()
    return getDetails(callService(f"{GEOLOCATION_SERVER}p/{ip}"))

def getIP(domain):
    return socket.gethostbyname(domain)

def ping(url):
    if url == "localhost":
        return 0
    start = time.time()
    try:
        readUrl(url)
    except:
        return FAIL
    return time.time() - start

sites = [
    "localhost", "rtlz.nl", "nos.nl", "reddit.com", "chrislaffra.com", "microsoft.com",
    "google.com", "apple.com", "mozilla.org", "wordpress.org", "en.wikipedia.org", "linkedin.com",
    "vimeo.com", "youtu.be", "github.com", "cnn.com", "paypal.com", "cnet.com",
    "dropbox.com", "wikimedia.org", "web.whatsapp.com", "happymac.app", "twitch.tv", "twitter.com",
]
        
def pingSite(site):
    return f"{site:19}", f"{ping(site):3.1f}s", getLocation(getIP(site))
        
def main():
    print("Locations:")
    print("-" * 80)
    for site in sites: print("  ".join(pingSite(site)))
    print("-" * 80)

if __name__ == "__main__":
    main()