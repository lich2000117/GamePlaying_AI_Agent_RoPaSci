from IG.search_algorithms import *
import random


<<<<<<< Updated upstream
# move token from start to end 
def move_token(symbol_type, start, end, play_dict):
    # move the token by adding new position
    play_dict["player"][symbol_type].remove(start)
    
=======
# return number of nodes count in player_class
# return:
#       {"s": 4, "r":2, "p":1}      #4 Scissors, 2 rock, 1 paper
def get_current_player_nodes_count(player_class, player_side):
    count_dict = {}
    count_dict["r"] = len(player_class.play_dict[player_side]["r"])
    count_dict["p"] = len(player_class.play_dict[player_side]["p"])
    count_dict["s"] = len(player_class.play_dict[player_side]["s"])
    return count_dict


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
    if point in find_player_symbols(play_dict, whichplayer, "p"):
        out += "p"
    if point in find_player_symbols(play_dict, whichplayer, "s"):
        out += "s"
    return out

# Remove all symbols of that type at that location
def remove_all_type_symbols_at_location(player_class, removetype, location):
    player_class.play_dict["player"][removetype] = \
                    list(filter(lambda a: a != location, player_class.play_dict["player"][removetype]))
    player_class.play_dict["opponent"][removetype] = \
                    list(filter(lambda a: a != location, player_class.play_dict["opponent"][removetype]))


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
>>>>>>> Stashed changes

# If two symbols place together, determine what to do with board_dict
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
        #symbol_type =   #need to call type look up
        start = action[1]
        end = action[2]
        move_token(symbol_type, start, end, self.play_dict)



