import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def get_empty_room(self, tab):
        room = 0
        empty_room = []
        while room < 8:
            i = 0
            empty = True
            while i < len(tab):
                if tab[i]["position"] == room:
                    empty = False
                i += 1
            if empty:
                empty_room.append(room)
            room += 1
        return empty_room

    def get_suspect_group(self, tab, shadow):
        i = 0
        suspect = []
        while i < len(tab):
            if tab[i][0]['position'] != shadow:
                suspect.append(tab[i])
            i += 1
        return suspect

    def get_group(self, tab):
        x = 0
        room = 0
        group = []
        while room < 8:
            current_group = []
            i = 0
            while i < len(tab):
                if tab[i]["position"] == room:
                    current_group.append(tab[i])
                i += 1
            if len(current_group) > 1:
                group.append(current_group)
                x += 1
            room += 1
        return group

    def select_character(self, suspect, data, fantom):
        x = 0
        while x < len(suspect) and x < len(data):
            i = 0
            while i < len(suspect[x]):
                if suspect[x][i]["color"] == fantom:
                    return x
                i += 1
            x += 1
        x = 0
        while x < len(suspect) and x < len(data):
            i = 0
            while i < len(suspect[x]):
                if suspect[x][i]["color"] == data[x]["color"]:
                    return x
                i += 1
            x += 1
        return random.randint(0, len(data) - 1)

    def select_position(self, empty_room, data):
        i = 0
        while i < len(data):
            x = 0
            while x < len(empty_room):
                if data[i] == empty_room[x]:
                    return i
                x += 1
            i += 1
        return 0

    def answer(self, question):
        # work
        state = question["game state"]
        if len(state) > 8:
            data = question["data"]
            group = self.get_group(state["characters"])
            suspect = self.get_suspect_group(group, state["shadow"])
            empty_room = self.get_empty_room(state["characters"])
            fantom = state["fantom"]
            qtype = question["question type"]
            response_index = random.randint(0, len(data) - 1)
            if qtype == "select character":
                response_index = self.select_character(suspect, data, fantom)
            if qtype == "select position":
                response_index = self.select_position(empty_room, data)
            # power = "activate " + data[response_inde]['color'] + " power"
            elif qtype == "activate purple power":
                response_index = 0
            elif qtype == "activate red power":
                response_index = 0
            elif qtype == "activate black power":
                response_index = 0
            elif qtype == "activate blue power":
                response_index = 0
            elif qtype == "activate white power":
                response_index = 0
            elif qtype == "activate grey power":
                response_index = 0
            elif qtype == "activate pink power":
                response_index = random.randint(0, len(data) - 1)
                print("respone : ", response_index)
            elif qtype == "select position":
                response_index = 0
                print("respone : ", response_index)
                j = 0
                while j < len(question["game state"]["characters"]):
                    print("gstate suspect : ", question["game state"]["characters"][j]["suspect"], " | position :",
                          question["game state"]["characters"][j]["position"], " | color : ",
                          question["game state"]["characters"][j]["color"])
                    x = 0
                    while x < len(data):
                        print(data[x])
                        if data[x] != question["game state"]["characters"][j]["position"]:
                            response_index = x
                            print("if response :", response_index)
                            x = 42
                        x += 1
                    j += 1


            # log
            fantom_logger.debug("|\n|")
            fantom_logger.debug("fantom answers")
            fantom_logger.debug(f"question type ----- {question['question type']}")
            fantom_logger.debug(f"data -------------- {data}")
            fantom_logger.debug(f"response index ---- {response_index}")
            fantom_logger.debug(f"response ---------- {data[response_index]}")
            return response_index
        return -1

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