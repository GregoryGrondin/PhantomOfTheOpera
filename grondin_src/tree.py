passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                 {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                 {7, 8, 4, 6}]

from grondin_src.gain import maximizer_gain, minimizer_gain 
from copy import deepcopy as dcpy

class Tree():
    def __init__(self, gamestate, data, configuration):
        self.bestGain = None
        self.gamestate = gamestate
        self.bestIndex = 0
        # print(configuration)

        # loop into each characters
        for index, char in enumerate(data):
            char_position = char['position']
            char_color = char['color']
            char_id = self.getCharId(char_color)
            blocked = gamestate['blocked']
            available_routes = self.getAvailableRoutes(char_position, char_color, blocked)
            bonus = 1 if (char_color == 'red') else 0
            # print("Char: %s, available routes: %s" % (char_color, available_routes))
            for room in available_routes:
                tmp = dcpy(gamestate)
                tmp["characters"][char_id]["position"] = room
                # evaluate gain when moving into a room
                # bonus is an improved strategy to prioritize if possible red character
                gain = maximizer_gain(tmp) + bonus 
                if (self.bestGain == None or gain > self.bestGain):
                    self.bestGain = gain
                    self.room = room
                    self.bestIndex = index
    
    def getBestCharIndex(self):
        return self.bestIndex
    
    def getBestRoom(self):
        return self.room
    
    # def characterNode(self, char_color, available_routes):
    #     # print('Color: %s, ID: %d' % (char_color, self.getCharId(char_color)))
    #     id = self.getCharId(char_color)
    #     self.gamestate['active character_cards'].pop(
    #         next(id for id, ch in enumerate(self.gamestate['active character_cards']) if ch['color'] == char_color)
    #     )

    def getCharId(self, color):
        for index, char in enumerate(self.gamestate['characters']):
            if char['color'] == color:
                return index
        return -1
    
    def getAvailableRoutes(self, char_position, char_color, blocked):
        routes = passages[char_position] if char_color != 'pink' else pink_passages[char_position]
        if char_position in blocked:
            routes = [r for r in routes if r not in blocked]
        return routes
