#!/usr/bin/env python

import os
import re
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

QUEUE_IN = 'firmware'
QUEUE_OUT = 'reports'
ANALYSIS = './analysis'

RABBIT_HOST = 'localhost'
RABBIT_PORT = 5672
RABBIT_USER = 'broker'
RABBIT_PASS = 'xl65x7jhacv'

### Handle Incoming Jobs ###

class Worker:
    def __init__(self, channel):
        self.channel = channel

    def callback(self, ch, method, properties, body):
        bodyHash = sha256(body).hexdigest()
        logger.info('Received new firmware job (%s)' % bodyHash)

        # Create directory for analysis
        path = tempfile.mkdtemp(
            prefix='temp.',
            suffix='.analysis'
        )
        logger.info('Created temp directory in %s' % path)

        distutils.dir_util.copy_tree(ANALYSIS, path)

        firm = os.path.join(path, 'firmware.bin') 

        with open(firm, 'w') as f:
            f.write(body)

        # Run analysis
        log = subprocess.Popen('binwalk -e -M -d 20 --directory=%s %s' % (path, firm), shell=True).wait()

        analyser = Analyser(os.path.join(path, "_firmware.bin.extracted"))

        result = {
            'hash': bodyHash,
            'log': str(log),
            'error': False,
            'analysis': analyser.generate_report()
        }
        logger.info('Analysis complete')

        for obj in glob.glob(os.path.join(path, '*.anal')):
            with open(obj, 'r') as f:
                raw = f.read().strip()

            if raw != '':
                result['analysis'].append(
                    json.loads(raw)
                )

        # Cleanup after analysis
        logger.info('Cleaning up')

        distutils.dir_util.remove_tree(path)

        # Add result to queue
        logger.info('Passing results')

        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_OUT,
            body=json.dumps(result)
        )
        
        # Acknowledge
        ch.basic_ack(delivery_tag=method.delivery_tag)
        

class Analyser:
    def __init__(self, path):
        logger.info("Created analyser with path " + path)
        self.path = path

    def generate_report(self):
        return [self.key_files(), self.key_strings()]#, self.check_php()]

    def check_php(self):
        struct = {
            'category': 'SQL injection',
            'name': 'SQL injection in PHP',
            'language': 'PHP',
            'findings': []
        }
        # Get php-reaper response
        print(self.path)
        resp, error = subprocess.Popen('/usr/bin/php --help')
        #resp, error = subprocess.Popen('/usr/bin/php ./analysis/php-reaper/php-reaper.php -d %s' % self.path).communicate()
        resp = resp.split("\n")
        # Parse response
        i = 0
        while i < len(resp):
            if resp[i].startWith("Potential SQL injections "):
                finding = {'severity': 'warning', 'file': resp[i].split("in file ")[1], 'text': ''}
                i += 1
                lines = []
                while i < len(resp) & resp[i] & (not resp[i].startWith("Potential SQL injections ")):
                    lines.append(resp[i].split(" ")[1].trim())
                    i += 1
                finding['text'] = 'Line(s): ' + ', '.join(lines)
                struct['findings'].append(finding)
        return struct

    def key_files(self):
        logger.info("Starting key_files")

        patterns =[
            '.ssh/.authorized_keys',
            'etc/shadow'
        ]

        files    = 0
        findings = []

        for dirpath, dirnames, filenames in os.walk(self.path):
            for name in filenames:
                files += 1
                path   = os.path.join(dirpath, name)
                for pattern in patterns:
                    if pattern in path:
                        print('found possible hardcoded key in %s' % path)
                        if not os.path.isfile(path):
                            continue
                        with open(path, 'r') as f:
                            text = 'Hardcoded key detected (possible backdoor)\n\n'
                            findings.append({
                                'severity': 'warning',
                                'file': path,
                                'text': text + f.read(),
                            })

        res = {
            'catagory': 'key material',
            'name': 'key file scan',
            'language': '',
            'findings': findings
        }

        print('processed %d files' % files)

        return res


    def key_strings(self):
        logger.info("Starting key_strings")

        private_keys = [
            re.compile('-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----', re.DOTALL),
            re.compile('-----BEGIN RSA PRIVATE KEY-----.*-----END RSA PRIVATE KEY-----', re.DOTALL),
            re.compile('-----BEGIN ENCRYPTED PRIVATE KEY-----.*-----END ENCRYPTED PRIVATE KEY-----', re.DOTALL)
        ]

        public_keys = [
            re.compile('-----BEGIN RSA PUBLIC KEY-----.*-----END RSA PUBLIC KEY-----', re.DOTALL),
            re.compile('-----BEGIN PUBLIC KEY-----.*-----END PUBLIC KEY-----', re.DOTALL)
        ]

        files    = 0
        findings = []

        for dirpath, dirnames, filenames in os.walk(self.path):
            for name in filenames:
                path = os.path.join(dirpath, name)

                if not os.path.isfile(path):
                    continue

                with open(path, 'r') as f:
                    raw = f.read()

                files += 1

                for rex in private_keys:
                    for key in rex.findall(raw):
                        #print 'private key found in %s' % path
                        text = ''
                        text += 'Private key detected\n\n'
                        text += key
                        findings.append({
                            'severity': 'danger',
                            'file': path,
                            'text': text
                        })

                for rex in public_keys:
                    for key in rex.findall(raw):
                        #print 'public key found in %s' % path
                        text = ''
                        text += 'Public key detected\n\n'
                        text += key
                        findings.append({
                            'severity': 'info',
                            'file': path,
                            'text': text
                        })


        res = {
            'catagory': 'key material',
            'name': 'key string scan',
            'language': '',
            'findings': findings
        }

        print('processed %d files' % files)

        return res


if __name__ == '__main__':
    ### Connect To RabbitMQ ###

    logger.info('Connecting to RabbitMQ')

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    parameters = pika.ConnectionParameters(
        RABBIT_HOST,
        RABBIT_PORT,
        '/',
        credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    worker = Worker(channel)

    ## Start Server

    logger.info('Server starting')

    channel.queue_declare(queue=QUEUE_IN)
    channel.queue_declare(queue=QUEUE_OUT)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(worker.callback, queue=QUEUE_IN)
    channel.start_consuming()
