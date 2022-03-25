import time

def open(name):
    return Database(name)

class Database(object):
    def __init__(self, name):
        self.name = name
        self.data = {}

    def read(self, key):
        # reading is fast
        time.sleep(0.001)
        return self.data.get(key, None)

    def write(self, key, value):
        # writing is slow
        time.sleep(0.01)
        self.data[key] = value

    def delete(self, key):
        time.sleep(0.005)
        del self.data[key]


def log(message):
    print(message)
    time.sleep(0.5)

def main():
    log("step 1. Create two books")
    book1 = open("book1")
    book2 = open("book2")
    count = 100
    keys = [f"key-{n}" for n in range(count)]
    values = [f"value-{n}" for n in range(count)]

    log("step 2. Write values to book 1")
    for key, value in zip(keys, values):
        book1.write(key, value)

    log("step 3. Copy values from book 1 to 2")
    for key in keys:
        value = book1.read(key)
        book2.write(key, value)

    log("step 4. Read values from book 2")
    for n in range(3):
        for key in keys:
            value = book2.read(key)

    log("step 5. Clear book 1")
    for key in keys:
        book1.delete(key)

    log("step 6. Done")

if __name__ == "__main__":
    main()