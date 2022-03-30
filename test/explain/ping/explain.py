import json
import sys
sys.path.extend(["../..", "../../.."]) # this module path is not needed when using pip install
import feynman;
from collections import defaultdict
import re


domains = {}
ips = {}
duration = {}

CARDS_PER_ROW = 6
CARD_SIZE = 12 # measured in vw
CARD_SPACING = 2 # measured in vw

@feynman.on("ping.getIP")
def getIP(domain):
    ip = feynman.return_value
    domains[ip] = domain
    ips[domain] = ip
    
def toVW(size):
    return f"{size}vw"

def getRowColumn():
    count = len(ips) - 1
    column = count % CARDS_PER_ROW
    row = round(count // CARDS_PER_ROW)
    return row, column
    
def getColor(ms):
    return "#8bbe1b" if ms < 300 else "#f8b878" if ms < 1000 else "#ff7f50" if ms < 1000 * ping.FAIL else "#ff4040"

def addCard(left, top, domain, ms):
    feynman.rectangle(toVW(left), toVW(top), toVW(CARD_SIZE), toVW(CARD_SIZE), background = getColor(ms))
    feynman.text(domain, toVW(left), toVW(top + CARD_SIZE/3), toVW(CARD_SIZE), 32, "center", "15px Arial", "black")
    latency = f"{ms:.0f}ms" if ms < 1000 * ping.FAIL else "FAILED"
    feynman.text(latency, toVW(left), toVW(top + CARD_SIZE/2), toVW(CARD_SIZE), 32, "center", "30px Arial", "black")

@feynman.on("ping.getLocation")
def getLocation(ip):
    row, column = getRowColumn()
    domain = domains[ip]
    ms = duration[domain] * 1000
    left = (CARD_SIZE + 2 * CARD_SPACING) * column + CARD_SPACING
    top = (CARD_SIZE + 2 * CARD_SPACING) * row + 3 * CARD_SPACING
    addCard(left, top, domain, ms)

@feynman.on("ping.ping")
def thisNameReallyDoesNotMatter(domain):
    duration[domain] = feynman.return_value

feynman.trace("ping")

print("running example.py with Feynman.Explain...")
with feynman.Explain():
    import ping
    ping.main()