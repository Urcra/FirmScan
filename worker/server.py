#!/usr/bin/env python

import os
import pika
import json
import glob
import logging
import tempfile
import subprocess
import distutils.dir_util

from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

QUEUE_IN  = 'firmware'
QUEUE_OUT = 'reports'
ANALYSIS  = './analysis'

RABBIT_HOST = 'localhost'
RABBIT_PORT = 5672
RABBIT_USER = 'broker'
RABBIT_PASS = 'xl65x7jhacv'

def fingerprint(s):
    return sha256(s).hexdigest()

### Handle Incoming Jobs ###

class Worker:
    def __init__(self, channel):
        self.channel = channel

    def callback(self, ch, method, properties, body):
        fp = fingerprint(body)

        logger.info('Received new firmware job (%s)' % fp)

        ## Create Directory For Analysis ##

        path = tempfile.mkdtemp(
            prefix = 'temp.',
            suffix = '.analysis'
        )

        logger.info('Created temp directory in %s' % path)

        distutils.dir_util.copy_tree(ANALYSIS, path)

        firm = os.path.join(path, 'firmware.bin')

        with open(firm, 'w') as f:
            f.write(body)

        ## Run Analysis ##

        log = subprocess.Popen('make -C %s -f root.mk analysis' % path, shell=True).wait()

        logger.info('Analysis complete, collecting findings')

        ## Extract Results ##

        result = {
            'hash': fp,
            'log': log,
            'error': False,
            'analysis': []
        }

        for obj in glob.glob(os.path.join(path, '*.anal')):
            with open(obj, 'r') as f:
                raw = f.read().strip()

            if raw != '':
                result['analysis'].append(
                    json.loads(raw)
                )

        ## Cleanup After Analysis ##

        logger.info('Cleaning up')

        distutils.dir_util.remove_tree(path)

        ## Add Result to Queue

        logger.info('Passing results')

        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_OUT,
            body=json.dumps(result)
        )

        # Acknowledge

        ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':

    ### Connect To RabbitMQ ###

    logger.info('Connecting to RabbitMQ')

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    parameters  = pika.ConnectionParameters(
        RABBIT_HOST,
        RABBIT_PORT,
        '/',
        credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel    = connection.channel()
    worker     = Worker(channel)

    ## Start Server

    logger.info('Server starting')

    channel.queue_declare(queue=QUEUE_IN)
    channel.queue_declare(queue=QUEUE_OUT)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(worker.callback, queue=QUEUE_IN)
    channel.start_consuming()
