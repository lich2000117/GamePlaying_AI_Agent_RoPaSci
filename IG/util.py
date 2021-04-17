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

#return a string for point's symbol given a location, two together means it has multiple symbol at that point
def get_symbol_by_location(whichplayer,play_dict,point):
    out = ""
    if point in find_player_symbols(play_dict, whichplayer, "r"):
        out += "r"
    elif point in find_player_symbols(play_dict, whichplayer, "p"):
        out += "p"
    elif point in find_player_symbols(play_dict, whichplayer, "s")::
        out += "s"
    return out



""" -------------------- PLAYER ACTION ---------------------"""
# Throw Action, reduce current throw number
def action_throw(symbol_type, point):
    return ("THROW",symbol_type, point)
# Slide Action
def action_slide(start, end):
    return ("SLIDE",start, end)
# Swing Action
def action_swing(start, end):
    return ("SWING",start, end)

#Initialize throw range, player: "lower" or "upper"
def Init_throw_range(player_class):
    if (player_class.side == "upper"):
        player_class.throw_range = range(4,5)
        player_class.side = "upper"
    else:
        player_class.throw_range = range(-4, -3)
        player_class.side = "lower"

# Update throw range for each player
def update_throw_range(player_class):
    # add throw range
    if len(player_class.throw_range) < 9:
        if (player_class.side == "upper"):
            player_class.throw_range = range(player_class.throws_left-5,5)
        else:
            player_class.throw_range = range(-4, 6-player_class.throws_left)

""" -------------------- PLAYER ACTION ---------------------"""



# If two symbols place together, determine what to do with play_dict
def eliminate_and_update_board(play_class, whichplayer, target_dict):

    # for each symbol of the player, find each one's counter symbol
    if whichplayer == "player":
        player1 = "player"
        player2 = "opponent"
    else:
        player2 = "player"
        player1 = "opponent"

    for symbol_type in play_class.play_dict[player1].keys():
        for symbol in play_class.play_dict[player1][symbol_type]:
            # # if Enemy has a symbol that can be eliminated by our player, remove opponent's symbol
            # if target_dict[symbol_type] == get_symbol_by_location("opponent", play_dict, symbol)
            #     play_dict.clear
            # look whether it will eliminate any opponent's symbol
            for token in reversed(play_class.play_dict[player2][target_dict[symbol_type]]):
                if symbol == token:
                    # remove opponent's token
                    play_class.play_dict[player2][target_dict[symbol_type]].remove(token)
                    # print("opponent's ", target_dict[type], token, "got eliminated\n")
            # look whether it will eliminate self's symbol
            for token in reversed(play_class.play_dict[player1][target_dict[symbol_type]]):
                if symbol == token:
                    play_class.play_dict[player1][target_dict[symbol_type]].remove(token)
        
            # look whether it will be eliminated by opponent
            for token in reversed(play_class.play_dict[player2][target_dict[target_dict[symbol_type]]]):
                if symbol == token:
                    # remove player's symbol
                    play_class.play_dict[player1][symbol_type].remove(symbol)
                    # print("player's ", type, symbol, "got eliminated\n")
            # look whether it will be eliminated by player's own symbol
            for token in reversed(play_class.play_dict[player1][target_dict[symbol_type]]):
                if symbol == token:
                    play_class.play_dict[player1][symbol_type].remove(symbol)
                    # print("player's ", type, symbol, "got eliminated by itself\n")



#update board according to player's action
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
    else:
        move_from = action[1]
        symbol_type = get_symbol_by_location(player,player_class.play_dict,move_from)
        assert(len(symbol_type) == 1)
        move_to = action[2]
        # move token from start to end, simply update play_dict
        #print("\n\n***\nstart:  ",move_from)
        #print("\n\n***\n type:  ",symbol_type)

        # move the token by adding new position and remove old one
        player_class.play_dict[player][symbol_type].remove(move_from)
        player_class.play_dict[player][symbol_type].append(move_to)
        

