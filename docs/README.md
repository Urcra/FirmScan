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
# Analysis
https://github.com/SmeegeSec/HashTag
