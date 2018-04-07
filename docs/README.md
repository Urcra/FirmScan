# Misc

`sha256` is used for generating fingerprints of firmware images

# RabbitMQ

## Queues

firmware : for submitting firmware to workers

reports : for relaying firmware reports back to the frontend

## Credentials

username : `broker` password : `xl65x7jhacv`

# JSON Schemas

## Report
```
{
  hash: "112233445566778899aa...",
  log: "[INFO] .... \n [ERROR] junk....",
  error: false,
  analysis: [
    {
       category: "linting"
       name: "binary imports (objdump)",
       language: "binary",
       findings: [
	 {
           severity: "warning",
           file: "./server",
           text: "import of gets(2) detected"
          }
          ...
       ]
    }
    ...
  ]
}
```

## Severity

The differnt severities that should be in the JSON are as follows:

* `"info"` : For informational findings. Colored blue on the frontend
* `"warning"`: For findings that are bad but not critical. Colored yellow on the frontend
* `"danger"` : For critical findings. Colored red on the frontend


# Analysis
General:

http://pmja.com.pl/iotsr.pdf (IoTInspector report)

https://github.com/SmeegeSec/HashTag


PHP:


https://github.com/exakat/php-static-analysis-tools
https://github.com/emanuil/php-reaper


JS:


https://github.com/ajinabraham/NodeJsScan


C:


https://www.dwheeler.com/flawfinder/
