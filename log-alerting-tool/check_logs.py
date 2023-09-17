#!/usr/bin/env python3
from config import ConfigLoader, CSV_COLUMN_DELIMITER
from datetime import datetime
from email_notifications import EmailService
from log_message import LogMessage
import argparse
import os
import re


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config", type=str, required=True)

    return parser.parse_args()


def get_messages_in_file(file, rule, regular_expressions) -> list:
    matches = []
    with open(file, "r") as log_file:
        log_file_text = log_file.read()
    for regex in regular_expressions:
        matches_for_regex = re.findall(regex, log_file_text)
        for match in matches_for_regex:
            matches.append(LogMessage(None, rule.name, format_match_str(match), datetime.now(), rule.send_notification))

    return matches


def format_match_str(match_str) -> str:
    return match_str.replace("\n", " ").replace(CSV_COLUMN_DELIMITER, "").strip()


def check_for_new_messages(rules_config) -> list:
    matches = []
    for rule in rules_config.rules:
        for file in rule.files:
            matches_from_file = get_messages_in_file(file, rule, rule.regular_expressions)
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


def write_to_file(file, messages):
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

    if len(included_messages) < 1:
        print("No email notification to send!")
        return

    print("Sending email notifications...")
    email_service = EmailService(email_configuration)
    email_service.send_email_notification(included_messages)
    print("Email notification sent!")


def run():
    args = parse_arguments()

    print(f"loading configuration from {args.config}...")
    configuration = ConfigLoader.load_config(args.config)

    print(f"Checking log files for new matching messages...")
    new_messages = check_for_new_messages(configuration.rules_configuration)
    print(f"{len(new_messages)} messages found!")

    print(f"filtering old messages that are already found")
    filtered_messages_by_id = exclude_existing_messages(configuration.messages_file, new_messages)
    new_messages = [msg for _, msg in  filtered_messages_by_id.items()]
    print(f"{len(new_messages)} new messages found!")

    send_notifications(configuration.email_configuration, new_messages)

    print(f"Writing {len(new_messages)} messages to file {configuration.messages_file}...")
    write_to_file(configuration.messages_file, new_messages)
    print("Done!")


if __name__ == '__main__':
    run()
