from collections import defaultdict
from threading import Thread
from TwitterAPI import TwitterAPI

ROTATE_RATE = 60 * 15  # 15 minutes
MIN_STORE_MENTIONS = 2  # Hashtag mentioned at least 2 times in ROTATE_RATE seconds

with open("keys.config", "r") as f:
    config = {}
    for line in f.readline():
        k, v = line.strip().split()
        config[k] = v

consumer_key = config["consumer_key"]
consumer_secret = config["consumer_secret"]
access_token = config["access_token"]
access_token_secret = config["access_token_secret"]

api = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)
hashtag_count = defaultdict(int)


def write_loop():
    global hashtag_count
    import time
    starttime = time.time()
    while True:
        time.sleep(ROTATE_RATE - ((time.time() - starttime) % ROTATE_RATE))
        local_count_copy = hashtag_count
        hashtag_count = defaultdict(int)
        with open("hashtags.{}".format(int(time.time())), "w") as f:
            for k, v in local_count_copy.items():
                if v < MIN_STORE_MENTIONS:
                    continue
                f.write("{} {}\n".format(k, v))

Thread(target=write_loop, name="Write Loop").start()

r = api.request('statuses/sample', {"language": "en"})
for item in r.get_iterator():
    if not "entities" in item or not "hashtags" in item["entities"]:
        continue
    hashtags = item["entities"]["hashtags"]
    if not hashtags:
        continue
    for hashtag_obj in hashtags:
        hashtag_count[hashtag_obj["text"]] += 1

    print(", ".join(["{}: {}".format(k, v) for k, v in hashtag_count.items() if v > 1]))
