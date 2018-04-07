import json

struct = {
    'category': 'dummy hard',
    'name': 'dummy',
    'language': 'dumlang',
    'findings': [
        {
            'severity': 'info',
            'file': './dummy',
            'text': 'https://www.youtube.com/watch?v=dP9Wp6QVbsk'
        }
    ]
}

print(json.dumps(struct))
