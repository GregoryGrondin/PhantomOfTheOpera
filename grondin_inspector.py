import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler
from grondin_src.gain import maximizer_gain, minimizer_gain 
# from gain import maximizer_gain, minimizer_gain
import protocol
from grondin_src.tree import Tree
host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)


class Player():

    def __init__(self):
        print("Grégory's amazing inspector AI")
        self.end = False
        self.gamestate = None
        self.functions = {
            "select character": self.choose_character,
            "activate": self.choose_power,
            "select position": self.choose_position,
        }
        # compute gain for a given configuration
        self.configurations = {
            1: [maximizer_gain],
            2: [maximizer_gain, minimizer_gain],
            3: [maximizer_gain, maximizer_gain, minimizer_gain],
            4: [maximizer_gain, minimizer_gain, minimizer_gain, maximizer_gain]
        }
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def choose_character(self, data):
        # Choose configuration given number of active characters
        configuration = self.configurations[len(data)]
        # Create a tree when choosing character
        self.tree = Tree(self.gamestate, data, configuration)
        # print(self.tree.getBestCharIndex())
        return self.tree.getBestCharIndex()
    
    def choose_power(self, data):
        # print("Choose power function")
        return random.randint(0, len(data)-1)
    
    def choose_position(self, data):
        # print("Choose position function")
        # index = data.index(self.tree.getBestRoom())
        try:
            return data.index(self.tree.getBestRoom())
        except ValueError:
            return random.randint(0, len(data)-1)
    
    def reset(self):
        self.socket.close()
    
    def getCarlottaPosition(self, gameState):
        position_carlotta = gameState["position_carlotta"]
        return position_carlotta
    
    def getActiveCharacterCards(self, gameState):
        character_cards = gameState["active character_cards"]
        return character_cards
    
    def getQuestionType(self, question):
        question_type = question["question type"]
        return question_type

    def getRedIndex(self, data):
        for idx, answer in enumerate(data):
            if (answer["color"] == "red"):
                return idx
        return random.randint(0, len(data)-1)

    def answer(self, question):
        # work
        data = question["data"]
        self.gamestate = question["game state"]
        # print('QT: %s' % self.getQuestionType(question))
        response_index = random.randint(0, len(data)-1)
        for qu in self.functions:
            if (self.getQuestionType(question).startswith(qu)) and self.functions[qu] is not None:
                response_index = self.functions[qu](data)
        # log
        inspector_logger.debug("|\n|")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()
p.run()
