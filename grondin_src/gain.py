# File to compute inspector gain

# Return a state of rooms with a dictionnary, first element is number of characters and second number of suspects
def rooms_count(gamestate):
    rooms = {
        0: [0, 0],
        1: [0, 0],
        2: [0, 0],
        3: [0, 0],
        4: [0, 0],
        5: [0, 0],
        6: [0, 0],
        7: [0, 0],
        8: [0, 0],
        9: [0, 0]
    }
    for char in gamestate['characters']:
        position = char['position']
        suspect = char['suspect']
        # nb of characters in a room
        rooms[position][0] += 1
        # nb of suspects in a room
        if suspect == True:
            rooms[position][1] += 1
    return rooms

# Return screamable and non screamable groups
def get_groups(gamestate):
    rooms = rooms_count(gamestate)
    shadow_pos = gamestate['shadow']
    screamable_group = 0
    non_screamable_group = 0

    # print('Rooms %s ' % rooms)
    # print('Shadow pos %s ' % shadow_pos)
    for room, values in rooms.items():
        if (values[0] == 1 or room == shadow_pos):
            screamable_group += values[1]
        elif (values[0] > 0):
            non_screamable_group += values[1]
    # print('Screamable: %d' % screamable_group)
    # print('Non screamable: %d' % non_screamable_group)
    return screamable_group, non_screamable_group


# Inspector try to have half screamable and half non_screamable group
# Worst gain = 0 and best = 8
def maximizer_gain(gamestate):
    screamable_group, non_screamable_group = get_groups(gamestate)
    # print('Screamable: %d' % screamable_group)
    # print('Non screamable: %d' % non_screamable_group)
    diff = non_screamable_group - screamable_group
    # add a bonus of 0.42 if most of players are grouped to prioritize grouping and avoid a scream
    bonus = 0.42 if diff > 0 else 0
    gain =  8 - abs(diff) + bonus
    # print('Gain %d' % gain)
    return gain

# Best gain = 0 and worst = 8
def minimizer_gain(gamestate):
    screamable_group, non_screamable_group = get_groups(gamestate)
    diff = non_screamable_group - screamable_group
    bonus = 0.42 if diff < 0 else 0
    gain = abs(diff) + bonus
    # print('Gain %d' % gain)
    return  gain 