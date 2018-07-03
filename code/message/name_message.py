from .message import Message


class NameMessage(Message):
    def __init__(self, name='', user_name=None):
        super().__init__(user_name)
        self.name = name.lower().replace(" ", "_")
