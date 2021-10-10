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


    def get_adjacent_positions(self, charact, game_state):
        passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
                    {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
        # ways for the pink character
        pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                        {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                        {7, 8, 4, 6}]
        if charact["color"] == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[charact["position"]] if set([room, charact["position"]]) != set(game_state["blocked"])]


    def get_adjacent_positions_from_position(self, position, charact, game_state):
        passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
                    {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
        # ways for the pink character
        pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                        {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                        {7, 8, 4, 6}]
        if charact["color"] == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[position] if set([room, position]) != set(game_state["blocked"])]

    def get_move_choices(self, game_state, character):
        # characters_in_room = [
        #     q for q in game_state["characters"] if q["position"] == character["position"]]
        # number_of_characters_in_room = len(characters_in_room)
        color = character['color']
        fantom_logger.debug(f"characters {color}")
        number_of_characters_in_room = 3

        # get the available rooms from a given position
        available_rooms = list()
        available_rooms.append(self.get_adjacent_positions(character, game_state))
        for step in range(1, number_of_characters_in_room):
            # build rooms that are a distance equal to step+1
            next_rooms = list()
            for room in available_rooms[step-1]:
                next_rooms += self.get_adjacent_positions_from_position(room,
                                                                        character,
                                                                        game_state)
            available_rooms.append(next_rooms)
        # flatten the obtained list
        temp = list()
        for sublist in available_rooms:
            for room in sublist:
                temp.append(room)
        # filter the list in order to keep an unique occurrence of each room
        temp = set(temp)
        available_positions = list(temp)

    def select_character(self, game_state, data):
        random_char = random.randint(0, len(data)-1)
        character = data[random_char]
        fantom_logger.debug(f"characterdfqsdfqsdfs {type(character)}")
        move_choices = self.get_move_choices(game_state, character)
        fantom_logger.debug(f"move choices  {move_choices}")


    def get_best_move(self, game_state, player, choices):
        max_value = -10
        characters = game_state["characters"]
        fantom_logger.debug(f"characters {type(characters)}")
        fantom = game_state['fantom']


    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        response_index = random.randint(0, len(data)-1)
        self.select_character(game_state, data)
        # log
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"game state -------------- {game_state}")
        fantom_logger.debug(f"question type ----- {question['question type']}")
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
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
