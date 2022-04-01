import db
import ping

domains = [ "google.com", "nos.nl", "facebook.com" ]

def main():
    servers = db.open("Servers")
    for domain in domains:
        servers.write(domain, ping.getIP(domain))
    print("Saved", len(domains), "domains")

if __name__ == "__main__":
    main()