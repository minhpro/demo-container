import json
import requests
import threading
import time

url = 'http://192.168.59.100:30080/test/heavy-greet'
headers = {'Host': 'example.com'}

def call_greet_heavy():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def call_request_thread():
    greet_response = call_greet_heavy()
    print(greet_response)

for i in range(20):
    print("Request: " + str(i))
    x = threading.Thread(target=call_request_thread)
    x.start()
    time.sleep(0.05)

