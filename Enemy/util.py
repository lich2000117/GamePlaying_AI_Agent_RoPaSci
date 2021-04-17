from IG.search_algorithms import *
import random


# return number of nodes count in player_class
# return:
#       {"s": 4, "r":2, "p":1}      #4 Scissors, 2 rock, 1 paper
def get_current_player_nodes_count(player_class):
    count_dict = {}
    count_dict["r"] = len(player_class.play_dict["player"]["r"])
    count_dict["p"] = len(player_class.play_dict["player"]["p"])
    count_dict["s"] = len(player_class.play_dict["player"]["s"])
    return count_dict

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

# params:
#           cur_point = (x_coordinate, y_coordinate)
# check if a point is not off the map)
def is_point_on_map(play_dict, cur_point):
    #check if off the map
    if abs(cur_point[0]) > 4 or abs(cur_point[1]) > 4:
        return False
    if abs(cur_point[0] + cur_point[1]) > 4:
        return False
    else:
        return True

#return a string for point's symbol given a location
def get_symbol_by_location(play_dict,point):
    if point in find_player_symbols(play_dict, "player", "r"):
        return "r"
    elif point in find_player_symbols(play_dict, "player", "p"):
        return "p"
    else:
        return "s"



""" -------------------- PLAYER ACTION ---------------------"""
# Throw Action, reduce current throw number
def action_throw(class_player, symbol_type, point):
    class_player.throws_left-=1
    return ("THROW",symbol_type, point)
# Slide Action
def action_slide(start, end):
    return ("SLIDE",start, end)
# Swing Action
def action_swing(start, end):
    return ("SWING",start, end)
""" -------------------- PLAYER ACTION ---------------------"""


# move token from start to end, simply add to play_dict, not checking elimination
def move_token(symbol_type, start, end, play_dict):
    # move the token by adding new position
    play_dict["player"][symbol_type].append(end)
    play_dict["player"][symbol_type].append(start)
    

# If two symbols place together, determine what to do with play_dict
def eliminate_and_update_board(play_dict, target_dict):
    for type in play_dict["player"].keys():
        # for each symbol of the player
        for symbol in play_dict["player"][type]:
            # look whether it can eliminate any opponent's symbol
            for token in play_dict["opponent"][target_dict[type]]:
                if symbol == token:
                    # remove opponent's token
                    play_dict["opponent"][target_dict[type]].remove(token)
                    # print("opponent's ", target_dict[type], token, "got eliminated\n")
            # look whether it will eliminate player's symbol
            for token in play_dict["player"][target_dict[type]]:
                if symbol == token:
                    # remove opponent's token
                    play_dict["player"][target_dict[type]].remove(token)
                    # print("player's ", target_dict[type], token, "got eliminated by itself\n")
        
            # look whether it will be eliminated
            for token in play_dict["opponent"][target_dict[target_dict[type]]]:
                if symbol == token:
                    # remove player's symbol
                    play_dict["player"][type].remove(symbol)
                    # print("player's ", type, symbol, "got eliminated\n")
            # look whether it will be eliminated by player's own symbol
            for token in play_dict["player"][target_dict[type]]:
                if symbol == token:
                    # remove player's token
                    play_dict["player"][type].remove(symbol)
                    # print("player's ", type, symbol, "got eliminated by itself\n")



#update board according to player's action
def put_action_to_board(player_class, player, action, play_dict):
    if action[0] in "THROW":
        #If throw, add a symbol onto board
        symbol_type = action[1]
        location = action[2]
        play_dict[player][symbol_type].append(location)
        #reduce available throw times by 1
        player_class.throws_left -= 1
    else:
        start = action[1]
        symbol_type = get_symbol_by_location(player_class.play_dict,start)
        end = action[2]
        move_token(symbol_type, start, end, player_class.play_dict)

