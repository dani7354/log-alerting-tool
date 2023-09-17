import json
import dataclasses

CSV_COLUMN_DELIMITER = ";"


@dataclasses.dataclass(frozen=True)
class EmailConfiguration:
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    mail_sender: str
    mail_recipient: str


@dataclasses.dataclass(frozen=True)
class Rule:
    name: str
    description: str
    send_notification: bool
    files: list[str]
    regular_expressions: list[str]


@dataclasses.dataclass(frozen=True)
class RulesConfiguration:
    rules: list[Rule]


@dataclasses.dataclass(frozen=True)
class Configuration:
    messages_file: str
    email_configuration: EmailConfiguration
    rules_configuration: RulesConfiguration


class ConfigLoader:
    @classmethod
    def load_rules(cls, file) -> RulesConfiguration:
        rules_config_dict = cls.load_from_json(file)
        rules = [Rule(r["name"], r["description"], r["send_notification"], r["files"], r["regular_expressions"])
                 for r in rules_config_dict["rules"]]

        return RulesConfiguration(rules)

    @classmethod
    def load_config(cls, config_file) -> Configuration:
        config_dict = cls.load_from_json(config_file)
        email_config = cls.load_email(config_dict)
        rules_config = cls.load_rules(config_dict["rules_file"])

        return Configuration(config_dict["messages_file"], email_config, rules_config)

    @staticmethod
    def load_email(config_dict) -> EmailConfiguration:
        email_config_dict = config_dict["email_settings"]

        return EmailConfiguration(
            email_config_dict["smtp_host"],
            email_config_dict["smtp_port"],
            email_config_dict["smtp_user"],
            email_config_dict["smtp_password"],
            email_config_dict["mail_sender"],
            email_config_dict["mail_recipient"])

    @staticmethod
    def load_from_json(file) -> dict:
        with open(file, "r") as json_file:
            return json.load(json_file)
