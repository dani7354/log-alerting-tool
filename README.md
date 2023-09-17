# log-alerting-tool
This Python script reads through log files and matches the lines against regular expressions defined
as rules in `log-alerting-tool/config/rules.json`. The log messages is saved
in a CSV file and sent as an email notification. 


## Usage
### check_logs.py
The script can be run from a terminal but is intended to be run as a cronjob:
```
$ ./log-alerting-tool/check_logs.py -c ./log-alerting-tool/config/configuration.json
```
__-c or --config__: Path to configuration file (required).
Configuration file format: `log-alerting-tool/config/configuration.json`.

### delete_old_messages.py
Script for deleting matching log messages older than the earliest modified time of the log files.
```
$ ./log-alerting-tool/delete_old_messages.py -c ./log-alerting-tool/config/configuration.json
```