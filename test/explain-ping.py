from collections import defaultdict
import sys
from xml.sax.handler import feature_namespace_prefixes
sys.path.append("..")
import feynman;

map = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/A_large_blank_world_map_with_oceans_marked_in_blue.PNG/2560px-A_large_blank_world_map_with_oceans_marked_in_blue.PNG"
feynman.image(0, 0, "100%", "100%", map)

domains = {}
ips = {}
locations = {}
duration = {}

CARDS_PER_ROW = 6
CARD_SIZE = 12 # measured in vw
CARD_SPACING = 2 # measured in vw

@feynman.on("ping.getIP")
def getIP(domain):
    ip = feynman.return_value
    domains[ip] = domain
    ips[domain] = ip

@feynman.on("ping.getLocation")
def getLocation(ip):
    count = len(ips) - 1
    column = count % CARDS_PER_ROW
    row = round(count // CARDS_PER_ROW)
    domain = domains[ip]
    ms = duration[domain] * 1000
    color = "#8bbe1b" if ms < 300 else "#f8b878" if ms < 1000 else "#ff7f50" if ms < 1000 * ping.FAIL else "#ff4040"
    locations[domain] = feynman.return_value
    def toVW(size):
        return f"{size}vw"
    def top(inc):
        return toVW((CARD_SIZE + 2 * CARD_SPACING) * row + 3 * CARD_SPACING + inc)
    left = toVW((CARD_SIZE + 2 * CARD_SPACING) * column + CARD_SPACING)
    feynman.rectangle(left, top(0), toVW(CARD_SIZE), toVW(CARD_SIZE), background = color)
    feynman.text(left, top(CARD_SIZE/3), domain, toVW(CARD_SIZE), 32, "center", "15px Arial", "black")
    latency = f"{ms:.0f}ms" if ms < 1000 * ping.FAIL else "FAILED"
    feynman.text(left, top(CARD_SIZE/2), latency, toVW(CARD_SIZE), 32, "center", "30px Arial", "black")

@feynman.on("ping.ping")
def _(domain):
    duration[domain] = feynman.return_value

print("running example.py with Feynman.Explain...")
with feynman.Explain():
    import ping
    ping.main()