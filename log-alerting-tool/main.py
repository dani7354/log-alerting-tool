#!/usr/bin/env python3
import argparse
import config
import datetime
import email_notifications
import log_message
import os
import re
import sys

CSV_COLUMN_DELIMITER = ";"

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config", type=str, required=True)

    return parser.parse_args()

def create_regex_patterns(regular_expressions) -> list:
    return [re.compile(regex) for regex in regular_expressions]

def line_is_match(line, regular_expressions) -> bool:
    for regex in regular_expressions:
        if regex.match(line):
            return True

    return False

def get_messages_in_file(file, rule, regular_expressions) -> list:
    matches = []
    with open(file, "r") as log_file:
        for line in log_file:
            if line_is_match(line, regular_expressions):
                matches.append(log_message.LogMessage(None, rule.name, line.rstrip(), datetime.datetime.now(), rule.send_notification))

    return matches

def check_for_new_messages(rules_config) -> list:
    matches = []
    for rule in rules_config.rules:
        regular_expressions = create_regex_patterns(rule.regular_expressions)
        for file in rule.files:
            matches_from_file = get_messages_in_file(file, rule, regular_expressions)
            matches.extend(matches_from_file)

    return matches

def exclude_existing_messages(matches_file, new_matches) -> dict:
    id_csv_index = 0
    new_matches_by_id = {m.id: m for m in new_matches}
    if not os.path.isfile(matches_file):
        return new_matches_by_id

    with open(matches_file, "r") as existing_matches_file:
        for line in existing_matches_file:
            line_split = line.split(CSV_COLUMN_DELIMITER)
            message_id = line_split[id_csv_index]
            if message_id in new_matches_by_id:
                del new_matches_by_id[message_id]

    return new_matches_by_id

def write_to_file(file, messages) -> None:
    if not os.path.isfile(file):
        with open(file, "w") as output_file:
            output_file.write(f"id"
                              f"{CSV_COLUMN_DELIMITER}type"
                              f"{CSV_COLUMN_DELIMITER}message"
                              f"{CSV_COLUMN_DELIMITER}added_date\n")

    with open(file, "a") as output_file:
        for m in messages:
            output_file.write(f"{m.id}"
                              f"{CSV_COLUMN_DELIMITER}{m.type_name}"
                              f"{CSV_COLUMN_DELIMITER}{m.message}"
                              f"{CSV_COLUMN_DELIMITER}{m.date_created}\n")

def send_notifications(email_configuration, messages):
    included_messages = []
    for m in messages:
        if m.send_notification:
            included_messages.append(m)

    email_service = email_notifications.EmailService(email_configuration)
    email_service.send_email_notification(included_messages)

def run():
    args = parse_arguments()

    print(f"loading configuration from {args.config}...")
    configuration = config.ConfigLoader.load_config(args.config)

    print(f"Checking log files for new matching messages...")
    new_messages = check_for_new_messages(configuration.rules_configuration)
    print(f"{len(new_messages)} messages found!")

    print(f"filtering old messages that are already found")
    filtered_messages_by_id = exclude_existing_messages(configuration.messages_file, new_messages)
    new_messages = [msg for _, msg in  filtered_messages_by_id.items()]
    print(f"{len(new_messages)} new messages found!")

    print("Sending email notifications...")
    send_notifications(configuration.email_configuration, new_messages)
    print("Notification sent!")

    print(f"Writing {len(new_messages)} messages to file {configuration.messages_file}...")
    write_to_file(configuration.messages_file, new_messages)
    print("Done!")


if __name__ == '__main__':
    try:
        run()
    except Exception as ex:
        print(ex)
        sys.exit(1)
