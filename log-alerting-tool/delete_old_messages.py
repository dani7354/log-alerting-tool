#!/usr/bin/env python3
from config import ConfigLoader, Rule, CSV_COLUMN_DELIMITER
from datetime import datetime
import argparse
import os


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config", type=str, required=True)

    return parser.parse_args()


def get_earliest_modified_date_for_logfiles(rules: list[Rule]) -> datetime:
    logfiles = set()
    for r in rules:
        for f in r.files:
            logfiles.add(f)
    modified_time = min([os.path.getmtime(f) for f in logfiles])

    return datetime.fromtimestamp(modified_time)


def delete_messages_before_date(matches_file_path: str, date: datetime) -> int:
    with open(matches_file_path, "r") as matches_file:
        lines = matches_file.readlines()
    lines_read = len(lines)
    lines_written = 0
    with open(matches_file_path, "w") as matches_file:
        for line in lines:
            line_split = line.split(CSV_COLUMN_DELIMITER)
            date_str = line_split[3].strip()
            date_from_line = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            if date_from_line >= date:
                lines_written += 1
                matches_file.write(line)

        return lines_read - lines_written


def main():
    args = parse_arguments()
    config_loader = ConfigLoader()

    print(f"loading configuration from {args.config}...")
    config = config_loader.load_config(args.config)

    print("Reading modified date for logfiles...")
    earliest_modified_date = get_earliest_modified_date_for_logfiles(config.rules_configuration.rules)

    print(f"Deleting messages before date {earliest_modified_date}...")
    delete_count = delete_messages_before_date(config.messages_file, earliest_modified_date)
    print(f"{delete_count} messages deleted!")


if __name__ == "__main__":
    main()
