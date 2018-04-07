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

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback, queue='hello', no_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
