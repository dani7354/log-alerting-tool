import json

class EmailConfiguration:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_password, mail_sender, mail_recipient):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.mail_sender = mail_sender
        self.mail_recipient = mail_recipient

class Rule:
    def __init__(self, name, description, send_notification, files, regular_expressions):
        self.name = name
        self.description = description
        self.send_notification = send_notification
        self.files = files
        self.regular_expressions = regular_expressions

class RulesConfiguration:
    def __init__(self, rules):
        self.rules = rules

class Configuration:
    def __init__(self, messages_file, email_configuration, rules_configuration):
        self.messages_file = messages_file
        self.email_configuration = email_configuration
        self.rules_configuration = rules_configuration

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
