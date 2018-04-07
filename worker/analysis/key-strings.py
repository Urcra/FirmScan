import os
import re
import sys
import json

private_keys = map(re.compile, [
    '-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----',
    '-----BEGIN RSA PRIVATE KEY-----.*-----END RSA PRIVATE KEY-----',
    '-----BEGIN ENCRYPTED PRIVATE KEY-----.*-----END ENCRYPTED PRIVATE KEY-----'
])

public_keys = map(re.compile, [
    '-----BEGIN RSA PUBLIC KEY-----.*-----END RSA PUBLIC KEY-----.*',
    '-----BEGIN PUBLIC KEY-----.*-----END PUBLIC KEY-----'
])

files    = 0
findings = []

for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for name in filenames:
        path = os.path.join(dirpath, name)

        if not os.path.isfile(path):
            continue

        with open(path, 'r') as f:
            raw = f.read()

        files += 1

        for rex in private_keys:
            for key in rex.findall(raw):
                print 'private key found in %s' % path
                text = ''
                text += 'Private key detected\n\n'
                text += key
                findings.append({
                    'severity': 'high',
                    'file': path,
                    'text': text
                })

        for rex in public_keys:
            for key in rex.findall(raw):
                print 'public key found in %s' % path
                text = ''
                text += 'Public key detected\n\n'
                text += key
                findings.append({
                    'severity': 'info',
                    'file': path,
                    'text': text
                })


res = {
    'category': 'key material',
    'name': 'key string scan',
    'language': '',
    'findings': findings
}

print 'processed %d files' % files

with open('key-strings.anal', 'w') as f:
    f.write(json.dumps(res))
