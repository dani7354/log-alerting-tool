from hashlib import sha256

class LogMessage:
    def __init__(self, id, type_name, message, date_created):
        self.type_name = type_name
        self.message = message
        self.date_created = date_created
        self.id = id if id is not None else self._generate_id()

    def __eq__(self, other):
        if isinstance(other, LogMessage):
            return self.id == other.id
        return False

    def __str__(self):
        return f"Hash: {self.id} Type: {self.type_name} Message: {self.message} Date: {self.date_created}"

    def _generate_id(self):
        return sha256(f"{self.type_name}{self.message}".encode("ascii")).hexdigest()