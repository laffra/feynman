import time

def open(name):
    return Database(name)

class Database(object):
    def __init__(self, name):
        self.name = name
        self.data = {}

    def read(self, key):
        # reading is fast
        time.sleep(0.000007)
        return self.data.get(key, None)

    def write(self, key, value):
        # writing is slow
        time.sleep(0.00007)
        self.data[key] = value

    def delete(self, key):
        time.sleep(0.000085)
        del self.data[key]

    def size(self):
        return len(self.data)


def log(message):
    print(message)

def main():
    when = time.time()
    log("step 1. Create two books")
    book1 = open("book1")
    book2 = open("book2")
    count = 10000
    keys = [f"key-{n}" for n in range(count)]
    values = [f"value-{n}" for n in range(count)]

    time.sleep(1)

    log(f"step 2. Write {count} values to book 1")
    for key, value in zip(keys, values):
        book1.write(key, value)

    time.sleep(1.5)

    log(f"step 3. Copy {count} values from book 1 to 2")
    for key in keys:
        value = book1.read(key)
        book2.write(key, value)

    time.sleep(1.5)

    log(f"step 4. Read {count} values from book 2")
    for key in keys:
        value = book2.read(key)

    time.sleep(1.5)

    log("step 5. Clear book 1")
    for key in keys:
        book1.delete(key)

    log("step 6. Done")
    print("Ran for", time.time() - when, "seconds")

if __name__ == "__main__":
    main()