import os
import sys
import json

patterns =[
    '.ssh/.authorized_keys',
    'etc/shadow'
]

files    = 0
findings = []

for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for name in filenames:
        files += 1
        path   = os.path.join(dirpath, name)
        for pattern in patterns:
            if pattern in path:
                print 'found possible hardcoded key in %s' % path
                with open(path, 'r') as f:
                    text = 'Hardcoded key detected (possible backdoor)\n\n'
                    findings.append({
                        'severity': 'warning',
                        'file': path,
                        'text': text + f.read(),
                    })

res = {
    'category': 'key material',
    'name': 'key file scan',
    'language': '',
    'findings': findings
}

print 'processed %d files' % files

with open('key-files.anal', 'w') as f:
    f.write(json.dumps(res))
