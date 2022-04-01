import sys
sys.path.extend([".", "..", "../..", "../../.."])
import nested
import feynman

EXPLAIN_PING = False
EXPLAIN_DB = True

def message(text):
    feynman.text(text, 100, 100, 600, color="red")

if EXPLAIN_PING:
    import examples.ping.explain
else:
    message("Set EXPLAIN_PING to True to see ping explained")

if EXPLAIN_DB:
    import examples.db.explain
else:
    message("Set EXPLAIN_DB to True to see db explained")

if __name__ == "__main__":
    with feynman.Explain():
        nested.main()