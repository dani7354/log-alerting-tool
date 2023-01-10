# log-alerting-tool
This Python script reads through log files and matches the lines against regular expressions defined
as rules in `log-alerting-tool/config/rules.json`. The log messages is saved
in a CSV file and sent as an email notification. 


## Usage
The script can be run from a terminal but is intended to be run as a cronjob:
```
$ ./log-alerting-tool/main.py -c ./log-alerting-tool/config/configuration.json
```
__-c or --config__: Path to configuration file (required).
Configuration file format: `log-alerting-tool/config/configuration.json`.