import json
import subprocess

struct = {
    'category': 'SQL injection',
    'name': 'SQL injection in PHP',
    'language': 'PHP',
    'findings': []
}
# Get php-reaper response
resp, error = subprocess.Popen('php ./analysis/php-reaper/php-reaper.php -d ./', shell=True).communicate()
resp = resp.split("\n")
# Parse response
i = 0
result = ""
while i < len(resp):
    line = resp[i]
    if line.startWith("Potential SQL injections "):
        finding = {'severity': 'warning', 'file': line.split("in file ")[1], 'text': ''}
        i += 1
        lines = []
        while i < len(resp) & resp[i] & (not resp[i].startWith("Potential SQL injections ")):
            lines.append(resp[i].split(" ")[1].trim())
            i += 1
        finding['text'] = 'Line(s): ' + ', '.join(lines)
        struct['findings'].append(finding)
print(struct)

