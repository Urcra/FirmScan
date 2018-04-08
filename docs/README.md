# RabbitMQ

## Queues

firmware : for submitting firmware to workers

reports : for relaying firmware reports back to the frontend

## Credentials

username : `broker` password : `xl65x7jhacv`

Change if not used locally

# JSON Schemas

## Report structure
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

The different severities that should be in the JSON are as follows:

* `"info"` : For informational findings. Colored blue on the frontend
* `"warning"`: For findings that are bad but not critical. Colored yellow on the frontend
* `"danger"` : For critical findings. Colored red on the frontend

# Misc

`sha256` is used for generating fingerprints of firmware images


# Potendial analysis modules
General:

http://pmja.com.pl/iotsr.pdf (IoTInspector report)

https://github.com/SmeegeSec/HashTag


PHP:


https://github.com/exakat/php-static-analysis-tools
https://github.com/emanuil/php-reaper


JS:


https://github.com/ajinabraham/NodeJsScan


C:

# Related work / Resources
https://github.com/attify/firmware-analysis-toolkit

https://github.com/misterch0c/firminator_backend

http://firmware.re/

https://www.iot-inspector.com/

https://firmalyzer.com/

https://github.com/mre/awesome-static-analysis

# Example firmware images

http://www.bluesound.com/wp-content/uploads/2018/04/V510_usb_stick_2.16.9.zip

https://www.dwheeler.com/flawfinder/

https://kb.netgear.com/31417/D6000-Firmware-Version-1-0-0-61
