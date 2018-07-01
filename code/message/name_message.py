from .message import Message


class NameMessage(Message):
    def __init__(self, name):
        self.name = name.lower().replace(" ", "_")
