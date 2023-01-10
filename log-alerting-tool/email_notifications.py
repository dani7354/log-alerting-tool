from bs4 import BeautifulSoup, Tag
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import socket
import ssl
import os.path

EMAIL_HTML_TEMPLATE = f"{os.path.abspath(os.path.dirname(__file__))}/html/email_notification.html"
EMAIL_SUBJECT = "log alerting tool"
HTML_TABLES_DIV_ID = "messages"
HTML_HEADING_ID = "heading"
HTML_TABLE = "table"
HTML_MESSAGE_HEADING = "h1"
HTML_TABLE_HEADING = "h2"
HTML_TR = "tr"
HTML_TD = "td"

class EmailService:
    def __init__(self, email_configuration):
        self.email_configuration = email_configuration

    def _create_message_str(self, new_messages) -> MIMEText:
        messages_by_type = self._get_messages_by_type(new_messages)
        email_body = self._read_html_template(EMAIL_HTML_TEMPLATE)

        soup = BeautifulSoup(email_body, "html.parser")
        self._insert_heading(soup)

        tables_div = soup.select_one(f"#{HTML_TABLES_DIV_ID}")

        for type_name, msgs in messages_by_type.items():
            heading, tables_tag =  self._create_table(soup, type_name, msgs)
            tables_div.append(heading)
            tables_div.append(tables_tag)

        mime_text_message = MIMEText(soup.__str__(), "html", "utf-8")
        subject = f"{EMAIL_SUBJECT}: {len(new_messages)} nye log-beskeder."
        mime_text_message["Subject"] = Header(subject, "utf-8")
        mime_text_message["From"] = self.email_configuration.mail_sender
        mime_text_message["To"] = self.email_configuration.mail_recipient

        return mime_text_message

    @classmethod
    def _create_table(cls, soup,  type_name, messages) -> tuple:
        heading = cls._create_heading_for_table(soup, type_name)
        table_tag = soup.new_tag(HTML_TABLE)

        for new_message in messages:
            table_row = cls._create_table_row(soup, new_message)
            table_tag.append(table_row)

        return heading, table_tag

    @staticmethod
    def _insert_heading(soup):
        hostname = socket.gethostname()
        heading_tag = soup.select_one(f"#{HTML_HEADING_ID}")
        heading_tag.string = f"Nye log-beskeder fra {hostname}"

    @staticmethod
    def _create_table_row(soup, message) -> Tag:
        tr_tag = soup.new_tag(HTML_TR)

        date_td = soup.new_tag(HTML_TD)
        date_td.string = str(message.date_created)

        message_td = soup.new_tag(HTML_TD)
        message_td.string = message.message

        tr_tag.append(date_td)
        tr_tag.append(message_td)

        return tr_tag

    def _send_email(self, email_str):
        context = ssl.create_default_context()
        with smtplib.SMTP(host=self.email_configuration.smtp_host, port=self.email_configuration.smtp_port) as mail_server:
            mail_server.starttls(context=context)
            mail_server.login(self.email_configuration.smtp_user, self.email_configuration.smtp_password)
            mail_server.send_message(email_str)

    def send_email_notification(self, new_messages):
        if len(new_messages) == 0:
            return

        email_str = self._create_message_str(new_messages)
        self._send_email(email_str)

    @staticmethod
    def _get_messages_by_type(messages) -> dict:
        messages.sort(key=lambda m: m.date_created)
        messages_by_type = {}
        for m in messages:
            if not m.type_name in messages_by_type:
                messages_by_type[m.type_name] = []
            messages_by_type[m.type_name].append(m)

        return messages_by_type
    @staticmethod
    def _read_html_template(path) -> str:
        with open(path, "r", encoding="utf-8") as template_file:
            template = template_file.read()

            return template

    @staticmethod
    def _create_heading_for_table(soup, type_name) -> Tag:
        heading = soup.new_tag(HTML_TABLE_HEADING)
        heading.string = type_name

        return heading
