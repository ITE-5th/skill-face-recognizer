# File Path Manager
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import socket
import sys

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill
from mycroft.util.log import LOG

# from .code.message.add_person_message import AddPersonMessage
# from .code.message.register_face_recognition_message import RegisterFaceRecognitionMessage
from .code.misc.camera import Camera
# from .code.misc.http.api import get_http_request_type
# from .code.misc.http.api import request_http
from .code.misc.receiver import Receiver
from .code.misc.sender import Sender
from .default_config import DefaultConfig

# TODO: Make sure "." before module name is not missing

LOG.warning('Running Skill Face Recognizer On Python ' + sys.version)

try:
    import picamera
except ImportError:
    # re-install yourself
    from msm import MycroftSkillsManager

    msm = MycroftSkillsManager()
    msm.install("https://github.com/ITE-5th/skill-face-recognizer")


class FaceRecognizerSkill(MycroftSkill):
    def __init__(self):
        super(FaceRecognizerSkill, self).__init__("FaceRecognizerSkill")
        LOG.warning('Running Skill Face Recognizer')

        if "server_url" not in self.settings:
            self.settings["server_url"] = DefaultConfig.server_url
        self.name = None
        self.socket = None
        self.receiver = None
        self.sender = None
        self.port = None
        self.host = None
        self.camera = Camera(width=800, height=600)
        self.connection_type = DefaultConfig.connection_type
        self.registered = False
        self.new_person = None
        # self.connect()

    def initialize(self):
        LOG.info('initializer')
        recognize_intent = IntentBuilder("FaceRecognizerIntent").require("Face").build()
        self.register_intent(recognize_intent, self.handle_recognize_intent)

    # def connect(self):
    #     try:
    #         self.connection_type = self.settings.get("connection_type", DefaultConfig.connection_type)
    #         self.host = self.settings.get("server_url", DefaultConfig.server_url)
    #         # LOG.info('settings server : ' + self.settings.get("server_url"))
    #         self.host = DefaultConfig.server_url
    #         self.port = DefaultConfig.FACE_RECOGNITION_PORT
    #         if self.connection_type == 'socket':
    #             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             LOG.info('connecting to server:' + self.host + ' : ' + str(self.port))
    #             self.socket.connect((self.host, self.port))
    #             self.receiver = Receiver(self.socket, json=True)
    #             self.sender = Sender(self.socket, json=True)
    #             #
    #             LOG.info('connected to server:' + self.host + ' : ' + str(self.port))
    #
    #     except Exception as e:
    #         LOG.warning(str(e))
    #
    # def send_recv(self, msg, user_name=DefaultConfig.name, target_name=None):
    #     if self.connection_type == 'http':
    #         url, method = get_http_request_type(msg, user_name, target_name)
    #         url = self.host + url
    #         return request_http(url, method, msg)
    #     else:
    #         sent = self.ensure_send(msg)
    #         if not sent:
    #             return None
    #         result = self.receiver.receive()
    #         return result

    # def register_face(self):
    #     LOG.info("register face")
    #     if self.registered:
    #         return True
    #
    #     self.name = self.settings.get('name', DefaultConfig.name)
    #
    #     msg = RegisterFaceRecognitionMessage(self.name)
    #     result = self.send_recv(msg)
    #     if not result:
    #         self.speak_dialog('RegisterError')
    #         return False
    #
    #     LOG.info(result)
    #     self.speak_dialog("AddResult", self.new_person)
    #     self.registered = True
    #     return True
    #
    # def ensure_send(self, msg):
    #     retries = 3
    #     while retries > 0:
    #         try:
    #             retries -= 1
    #             self.sender.send(msg)
    #             break
    #         except Exception as e:
    #             if retries <= 0:
    #                 LOG.warning('Cannot Connect')
    #                 self.speak('Cannot Connect')
    #                 return False
    #             self.connect()
    #             LOG.warning(str(e))
    #     return True

    def handle_recognize_intent(self, message):
        # try:
        #     image, _ = self.camera.take_image()
        #     msg = FaceRecognitionMessage(image=image)
        #     sent = self.ensure_send(msg)
        #     if not sent:
        #         self.speak_dialog('RegisterError')
        #         return False
        #
        #     response = self.receiver.receive()
        #     LOG.info(response)
        #     result = self.handle_message(response.get('result'))
        #     self.speak_dialog("result", result)
        #
        # except Exception as e:
        #     LOG.info('Something is wrong')
        #     LOG.info(str(e))
        #     LOG.info(str(traceback.format_exc()))
        #     self.speak("Exception")
        #     self.connect()
        #     return False
        LOG.info('recognize')

        return True

    # @intent_handler(IntentBuilder("FaceIntent").require('add').require('name'))
    # def add(self, message):
    #     if not self.registered:
    #         registered = self.register_face()
    #         if not registered:
    #             return False
    #     LOG.info(message.data)
    #     self.new_person = message.data.get('name')
    #     return True
    #
    # @intent_handler(IntentBuilder("FaceIntent").require('capture'))
    # def capture(self, message):
    #     if not self.registered:
    #         registered = self.register_face()
    #         if not registered:
    #             return False
    #     if self.new_person is None:
    #         self.speak('Please add person before capture')
    #         return True
    #     image, _ = self.camera.take_image(1)
    #     if image is None:
    #         self.speak_dialog("PersonCountError")
    #         return True
    #     msg = AddPersonMessage(image)
    #     # sent = self.ensure_send(msg)
    #     result = self.send_recv(msg)
    #     if not result:
    #         return False
    #     # result = self.receiver.receive()
    #     LOG.info(result)
    #     self.speak_dialog("AddResult")
    #
    #     self.images_count += self.images_count
    #     if self.images_count > DefaultConfig.MaxImagesCount:
    #         self.new_person = None
    #
    #     return True

    @staticmethod
    def handle_message(response):
        """
        converts server response to meaningful sentence
        :param response: string of people names includes unknown
        :return: dictionary contains sentence in result
        """
        unknown = 'Unknown'
        persons = response.split(',')
        unk_count = sum([x.split(' ').count(unknown) for i, x in enumerate(persons)])

        # remove Unknown
        persons = [x for i, x in enumerate(persons) if x.split(' ')[0] != unknown]
        for idx, person in enumerate(persons):
            person = person.split(' ')
            persons[idx] = person[0].replace('_', ' ').title()
            persons[idx] += ' . '
            # persons[idx] += ' With probability of {} Percent . '.format(person[1])

        if unk_count > 0:
            persons.append(str(unk_count) + ' Unknown persons . ')

        persons_count = len(persons)
        phrase = ''
        for i in range(persons_count):
            phrase += persons[i]
            phrase += ' and ' if i == persons_count - 2 and persons_count > 1 else ''
        return {'result': phrase}

    def stop(self):
        super(FaceRecognizerSkill, self).shutdown()
        LOG.info("Face Recognizer Skill CLOSED")
        if self.socket:
            self.socket.close()


def create_skill():
    return FaceRecognizerSkill()
