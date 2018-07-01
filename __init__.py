# File Path Manager
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import socket
import sys
import traceback

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.util.log import LOG

from .code.message.face_recognition_message import FaceRecognitionMessage
from .code.misc.camera import Camera
from .code.misc.receiver import Receiver
from .code.misc.sender import Sender
from .default_config import DefaultConfig

# TODO: Make sure "." before module name is not missing

LOG.warning('Running Skill Question Answering On Python ' + sys.version)

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
            self.settings["server_url"] = "192.168.43.243"
        self.socket = None
        self.receiver = None
        self.sender = None
        self.port = None
        self.host = None
        self.camera = Camera(width=800, height=600)
        self.connect()

    def connect(self):
        try:
            self.port = DefaultConfig.FACE_RECOGNITION_PORT
            self.host = self.settings.get("server_url", DefaultConfig.server_url)
            LOG.info("Face Recognizer Skill started " + self.host + ":" + str(self.port))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.receiver = Receiver(self.socket, json=True)
            self.sender = Sender(self.socket, json=True)
            LOG.info('connected to server:' + self.host + ' : ' + str(self.port))
        except Exception as e:
            LOG.warning(str(e))

    def ensure_send(self, msg):
        retries = 3
        while retries > 0:
            try:
                retries -= 1
                self.sender.send(msg)
                break
            except Exception as e:
                if retries <= 0:
                    LOG.warning('Cannot Connect')
                    self.speak('Cannot Connect')
                    return False
                self.connect()
                LOG.warning(str(e))
        return True

    @intent_handler(IntentBuilder("FaceRecognizerIntent").require('face'))
    def recognise(self, message):
        try:
            image, _ = self.camera.take_image()
            msg = FaceRecognitionMessage(image=image)
            sent = self.ensure_send(msg)
            if not sent:
                self.speak_dialog('RegisterError')
                return False

            response = self.receiver.receive()
            LOG.info(response)
            result = self.handle_message(response.get('result'))
            self.speak_dialog("result", result)

        except Exception as e:
            LOG.info('Something is wrong')
            LOG.info(str(e))
            LOG.info(str(traceback.format_exc()))
            self.speak("Exception")
            self.connect()
            return False
        return True

    @staticmethod
    def handle_message(response):
        """
        converts server response to meaningful sentence
        :param response: string of answers
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
