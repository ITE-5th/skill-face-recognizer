import json
import _pickle as pickle


class Receiver:

    def __init__(self, socket, json=True):
        self.socket = socket

        if json:
            self.receive = self.receive_json
        else:
            self.receive = self.receive_pickle

    def receive(self):
        pass

    def receive_pickle(self):
        view = self._receive()
        try:
            deserialized = pickle.loads(view)
        except (TypeError, ValueError) as e:
            raise Exception('Data received was not in JSON format')
        return deserialized

    def receive_json(self):
        view = self._receive()
        view = view.decode()
        try:
            deserialized = json.loads(view)
        except (TypeError, ValueError) as e:
            raise Exception('Data received was not in JSON format')
        return deserialized

    def _receive(self):
        # read the length of the data, letter by letter until we reach EOL
        length_str = ''
        char = self.socket.recv(1).decode()
        if char == '':
            return char
        while char != '\n':
            length_str += char
            char = self.socket.recv(1).decode()
        total = int(length_str)
        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = self.socket.recv_into(view[next_offset:], total - next_offset)
            next_offset += recv_size
        view = view.tobytes()
        return view
