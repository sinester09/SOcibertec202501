import requests
import threading
import argparse
import time
from queue import Queue

# Variables globales
request_counter = 0
timer=9
printed_msgs = set()
lock = threading.Lock()

def print_msg(msg):
    global printed_msgs
    with lock:
        if msg not in printed_msgs:
            print("\n{} after {} requests".format(msg, request_counter))
            printed_msgs.add(msg)

def handle_status_codes(status_code):
    global request_counter
    with lock:
        request_counter += 1
        print("\r{} requests have been sent".format(request_counter), end="")
        if status_code == 429:
            print_msg("You have been throttled")
        elif status_code == 500:
            print_msg("Status code 500 received")

def send_request(method, url, payload=None):
    try:
        time.sleep(timer)
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, data=payload, timeout=5)
        handle_status_codes(response.status_code)
    except requests.RequestException as e:
        print(f"\nError: {e}")

def worker(queue, method, url, payload):
    while not queue.empty():
        queue.get()
        send_request(method, url, payload)
        queue.task_done()

def main():
    parser = argparse.ArgumentParser(description="HTTP Request Flooder")
    parser.add_argument("-g", "--get", help="Specify GET request URL")
    parser.add_argument("-p", "--post", help="Specify POST request URL")
    parser.add_argument("-d", "--data", help="Specify payload data for POST request")
    parser.add_argument("-f", "--file", help="Specify payload file for POST request")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use")
    args = parser.parse_args()

    if not (args.get or args.post):
        parser.error("You must specify either --get or --post.")

    method = "GET" if args.get else "POST"
    url = args.get or args.post
    payload = None

    if args.data:
        payload = args.data
    elif args.file:
        try:
            with open(args.file, "r") as f:
                payload = f.read()
        except FileNotFoundError:
            print("Error: File not found.")
            return

    queue = Queue()
    for _ in range(args.threads * 10):  # Adjust the number of requests as needed
        queue.put(None)

    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(queue, method, url, payload))
        thread.start()
        threads.append(thread)

    queue.join()

    for thread in threads:
        thread.join()

    print("\nFinished sending requests.")

if __name__ == "__main__":
    main()

