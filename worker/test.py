import sys

from server import *

class CH:
    def __init__(self):
        pass

    def basic_ack(self, delivery_tag):
        pass

class METHOD:
    def __init__(self):
        pass

    def delivery_tag(self):
        return 'lol'

class CHANNEL:
    def basic_publish(self, exchange, routing_key, body):
        print exchange, routing_key, body


ch = CH()
method = METHOD()
channel = CHANNEL()
properties = None

with open(sys.argv[1], 'r') as f:
    body = f.read()

worker = Worker(channel)
worker.callback(ch, method, properties, body)
