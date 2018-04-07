#!/usr/bin/env python

import pika

credentials = pika.PlainCredentials('broker', 'xl65x7jhacv')
parameters  = pika.ConnectionParameters(
    'localhost',
    5672,
    '/',
    credentials
)

connection = pika.BlockingConnection(parameters)
channel    = connection.channel()
channel.queue_declare(queue='hello')
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body='Hello World!'
)

connection.close()
print(" [x] Sent 'Hello World!'")
