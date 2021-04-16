from IG.search_algorithms import *
import random


# move token from start to end 
def move_token(symbol_type, start, end, play_dict):
    # move the token by adding new position
    play_dict["player"][symbol_type].remove(start)
    

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



