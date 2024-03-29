from hashlib import sha256


class LogMessage:
    def __init__(self, id, type_name, message, date_created, send_notification):
        self.type_name = type_name
        self.message = message
        self.date_created = date_created
        self.send_notification = send_notification
        self.id = id if id else self._generate_id()

    def __eq__(self, other):
        if isinstance(other, LogMessage):
            return self.id == other.id
        return False

    def __str__(self):
        return f"Hash: {self.id} Type: {self.type_name} Message: {self.message} Date: {self.date_created}"

    def _generate_id(self):
        return sha256(f"{self.type_name}{self.message}".encode("utf-8")).hexdigest()
