# this function returns how many steps for a symbol to move the position of 
# another symbol, it takes the positions of two symbols as input
# from position1 to position2
    # p1 = (0,0)
    # p2 = (-1,-2)
    # print(least_distance(p1,p2), " step(s) between (", p1[0], p1[1] ,") and (", p2[0], p2[1], ")")
    
def least_distance(position1, position2):
    # case1: top-right area
    total_distance = 0
    if position2[0] >= position1[0] and position2[1] >= position1[1]:
        total_distance = position2[0] + position2[1] - position1[0] - position1[1]
    # case2: bot-left area
    elif position2[0] <= position1[0] and position2[1] <= position1[1]:
        total_distance = position1[0] + position1[1] - position2[0] - position2[1]
    # case3: bot-right area
    elif position2[0] < position1[0] and position2[1] > position1[1]:
        total_distance = max(position1[0] - position2[0], position2[1] - position1[1])
    # case4: top-left area
    else:
        total_distance = max(position2[0] - position1[0], position1[1] - position2[1])
    return total_distance


#Initialize throw range, player: "lower" or "upper"
def Init_throw_range(player_class):
    if (player_class.side == "upper"):
        player_class.throw_range = range(4, 5)
        player_class.enemy_throw_range = range(-4, -3)
    else: 
        player_class.throw_range = range(-4, -3)
        player_class.enemy_throw_range = range(4, 5)


def update_throw_range(player_class):
    # add throw range
    if len(player_class.throw_range) < 9:
        if (player_class.side == "upper"):
            player_class.throw_range = range(player_class.throws_left-5,5)
        else:
            player_class.throw_range = range(-4, 6-player_class.throws_left)


def add_action_to_play_dict(player_class, player, action):
    if action[0] in "THROW":
        #If throw, add a symbol onto board
        symbol_type = action[1]
        location = action[2]
        player_class.play_dict[player][symbol_type].append(location)
        #reduce available throw times by 1
        if player == "opponent":
            player_class.enemy_throws_left -= 1
        else:
            player_class.throws_left -= 1
        update_throw_range(player_class)
    else:
        move_from = action[1]
        symbol_type = get_symbol_by_location(player, player_class.play_dict, move_from)
        move_to = action[2]
        # move token from start to end, simply update play_dict

        # move the token by adding new position and remove old one
        player_class.play_dict[player][symbol_type].remove(move_from)
        player_class.play_dict[player][symbol_type].append(move_to)


# Find upper/lower player's all symbols given specific type
##    find_player_symbols(play_dict, "upper", "R") ------  find upper player's all rocks
#      return a list of tuples [(x,y),(x,y),(x,y)]
#       if the pocket is empty, return False
def find_player_symbols(play_dict, player_side, symbol_type):
    node_list = play_dict[player_side][symbol_type]
    if node_list:
        out = node_list.copy()
        return out
    else:
        return []


def get_symbol_by_location(whichPlayer, play_dict, point):
    out = ""
    if point in find_player_symbols(play_dict, whichPlayer, "r"):
        out += "r"
    if point in find_player_symbols(play_dict, whichPlayer, "p"):
        out += "p"
    if point in find_player_symbols(play_dict, whichPlayer, "s"):
        out += "s"
    return out


# If two symbols place together, determine what to do with play_dict
def eliminate_and_update_board(play_class,target_dict):
    # target_dict = {"r":"s", "s":"p", "p":"r"}
    # first find tokens that need to be eliminated
    for symbol_type, target_symbol in target_dict.items():
        #list of all locations of this type
        list_locations_of_type = play_class.play_dict["player"][symbol_type]\
                                + play_class.play_dict["opponent"][symbol_type]
        #Iterate Through the locations and remove its target_symbol
        for position in reversed(list_locations_of_type):
            #  get what types are at location, 
            types_at_location = set(get_symbol_by_location("player", play_class.play_dict, position)\
                    + get_symbol_by_location("opponent",play_class.play_dict, position))
            # if three types all occurs, remove all of the symbols of all types at that location
            if (len(types_at_location) == 3):
                remove_all_type_symbols_at_location(play_class,"s",position)
                remove_all_type_symbols_at_location(play_class,"r",position)
                remove_all_type_symbols_at_location(play_class,"p",position)
            remove_all_type_symbols_at_location(play_class, target_symbol, position)

# Remove all symbols of that type at that location
def remove_all_type_symbols_at_location(player_class, removetype, location):
    player_class.play_dict["player"][removetype] = \
                    list(filter(lambda a: a != location, player_class.play_dict["player"][removetype]))
    player_class.play_dict["opponent"][removetype] = \
                    list(filter(lambda a: a != location, player_class.play_dict["opponent"][removetype]))
        
