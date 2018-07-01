from .message import Message


class NameMessage(Message):
    def __init__(self, name):
        super().__init__()
        self.name = name.lower().replace(" ", "_")
