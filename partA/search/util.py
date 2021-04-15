"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains some helper functions for printing actions and boards.
Feel free to use and/or modify them to help you develop your program.
"""

# this function determines whether the game has ended depending on 
# the situation on the board

from search.search_algorithms import *
import random


def isGameEnded(board_dict):
    isLowerAlive = False
    # is there lower's symbol on the board
    for symbol in board_dict.values():

        if len(symbol) == 3:
            isLowerAlive = True

    if isLowerAlive:
        return False
    else:
        return True

#load json file data into board_dict:
        # Upper player:   R S P
        # Lower player:   (r), (s), (p)
        # Block tile :    BLOCK     
def load_json_data(board_dict, json_data):
    out_dict = {}
    #Load lower player's board data
    for item in json_data["lower"]:
        dict_key = tuple(item[1:])   #read coordinate data
        out_dict[dict_key] = "("+item[0]+")"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict)    #Need to check if the symbols were put together, using function below.

    #Load upper player's board data
    for item in json_data["upper"]:
        dict_key = tuple(item[1:])
        out_dict[dict_key] = item[0].upper()
        board_dict.update(out_dict)
    #Load Block board data
    for item in json_data["block"]:
        dict_key = tuple(item[1:])
        out_dict[dict_key] = "BLOCK"
        board_dict.update(out_dict)
    ### board_dict.update() simply update the dictionary,
    ### cannot handle the situation that symbols are placed into the same grid.
    ### Need to write a function to check dictionary using update_board_dict() function

def initialize_board_for_next_turn(next_board_dict, board_dict):
    for key in board_dict.keys():
        if len(board_dict[key]) == 3:
            next_board_dict["lower"][board_dict[key][1].upper()].append(key)
        elif len(board_dict[key]) == 5:
            next_board_dict["block"].append(key)


# If two symbols place together, determine what to do with board_dict
def update_board_dict(board_dict, new_dict, target_dict):
    for type in new_dict["upper"].keys():
        # for each symbol of the upper
        for symbol in new_dict["upper"][type]:
            # look whether it can eliminate any lower's symbol
            for token in new_dict["lower"][target_dict[type]]:
                if symbol == token:
                    # remove lower's token
                    new_dict["lower"][target_dict[type]].remove(token)
                    # print("lower's ", target_dict[type], token, "got eliminated\n")
            # look whether it will eliminate upper's symbol
            for token in new_dict["upper"][target_dict[type]]:
                if symbol == token:
                    # remove lower's token
                    new_dict["upper"][target_dict[type]].remove(token)
                    # print("upper's ", target_dict[type], token, "got eliminated by itself\n")
        
            # look whether it will be eliminated
            for token in new_dict["lower"][target_dict[target_dict[type]]]:
                if symbol == token:
                    # remove upper's symbol
                    new_dict["upper"][type].remove(symbol)
                    # print("upper's ", type, symbol, "got eliminated\n")
            # look whether it will be eliminated by upper's own symbol
            for token in new_dict["upper"][target_dict[type]]:
                if symbol == token:
                    # remove upper's token
                    new_dict["upper"][type].remove(symbol)
                    # print("upper's ", type, symbol, "got eliminated by itself\n")
            convert_to_board_dict(new_dict, board_dict)

def convert_to_board_dict(play_dict, board_dict):
    out_dict = {}
    #Load upper player's board data
    player_dict = play_dict["upper"]
    for R_coord in player_dict["R"]:
        dict_key = R_coord   #read coordinate data
        out_dict[dict_key] = "R"   #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict)    #Need to check if the symbols were put together, using function below.
    for P_coord in player_dict["P"]:
        dict_key = P_coord   #read coordinate data
        out_dict[dict_key] = "P"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict) 
    for S_coord in player_dict["S"]:
        dict_key = S_coord   #read coordinate data
        out_dict[dict_key] = "S"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict) 

    #Load lower player's board data
    player_dict = play_dict["lower"]
    for R_coord in player_dict["R"]:
        dict_key = R_coord   #read coordinate data
        out_dict[dict_key] = "("+"r"+")"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict)    #Need to check if the symbols were put together, using function below.
    for P_coord in player_dict["P"]:
        dict_key = P_coord   #read coordinate data
        out_dict[dict_key] = "("+"p"+")"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict) 
    for S_coord in player_dict["S"]:
        dict_key = S_coord   #read coordinate data
        out_dict[dict_key] = "("+"s"+")"    #set dictionary value
        board_dict.update(out_dict)         #update_board_dict(board_dict, out_dict) 

    #Load Block board data
    for Block_coord in play_dict["block"]:
        dict_key = Block_coord
        out_dict[dict_key] = "BLOCK"
        board_dict.update(out_dict)
    ### board_dict.update() simply update the dictionary,
    ### cannot handle the situation that symbols are placed into the same grid.
    ### Need to write a function to check dictionary using update_board_dict() function


# This function turns the board_dict into player_dict
def board_cognition(board_dict, player_dict):
    for key in board_dict.keys():
        if board_dict[key] == "R":
                player_dict["upper"]["R"].append(key)
        elif board_dict[key] == "P":
                player_dict["upper"]["P"].append(key)
        elif board_dict[key] == "S":
                player_dict["upper"]["S"].append(key)
        elif board_dict[key] == "(r)":
                player_dict["lower"]["R"].append(key)
        elif board_dict[key] == "(p)":
                player_dict["lower"]["P"].append(key)
        elif board_dict[key] == "(s)":
                player_dict["lower"]["S"].append(key)
        elif board_dict[key] == "BLOCK":
                player_dict["block"].append(key)

def move_token(type, start, end, next_board_dict, turn):
    # move the token by removing its early position and adding new position
    # next_board_dict["upper"][type].remove(start)
    next_board_dict["upper"][type].append(end)

    if(least_distance(start, end) == 1):
        print_slide(turn, start[0], start[1], end[0], end[1])
    elif (least_distance(start, end) == 2):
        print_swing(turn, start[0], start[1], end[0], end[1])
    else:
        print("wrong move: it did not move")
    
def random_move(type, start, play_dict, next_board_dict, turn):

    next_point_list = get_six_adj_nodes(start)
    upper_token_list = [item for sublist in play_dict["upper"].values() for item in sublist]
    for point in next_point_list:
        if point in upper_token_list:
            swing_node = []
            for node in get_six_adj_nodes(point):
                if least_distance(start, node) == 2:
                    swing_node.append(node)
            next_point_list = next_point_list + swing_node ## add swing nodes
    
    random.shuffle(next_point_list)
    for point in next_point_list:
        if is_point_valid(next_board_dict, point):
            if check_counter_node(next_board_dict, type, point):
                move_token(type, start, point, next_board_dict, turn)
                break

def print_slide(t, r_a, q_a, r_b, q_b, **kwargs):
    """
    Output a slide action for turn t of a token from hex (r_a, q_a)
    to hex (r_b, q_b), according to the format instructions.

    Any keyword arguments are passed through to the print function.
    """
    print(f"Turn {t}: SLIDE from {(r_a, q_a)} to {(r_b, q_b)}", **kwargs)


def print_swing(t, r_a, q_a, r_b, q_b, **kwargs):
    """
    Output a swing action for turn t of a token from hex (r_a, q_a)
    to hex (r_b, q_b), according to the format instructions.
    
    Any keyword arguments are passed through to the print function.
    """
    print(f"Turn {t}: SWING from {(r_a, q_a)} to {(r_b, q_b)}", **kwargs)


def print_board(board_dict, message="", compact=True, ansi=False, **kwargs):
    """
    For help with visualisation and debugging: output a board diagram with
    any information you like (tokens, heuristic values, distances, etc.).

    Arguments:

    board_dict -- A dictionary with (r, q) tuples as keys (following axial
        coordinate system from specification) and printable objects (e.g.
        strings, numbers) as values.
        This function will arrange these printable values on a hex grid
        and output the result.
        Note: At most the first 5 characters will be printed from the string
        representation of each value.
    message -- A printable object (e.g. string, number) that will be placed
        above the board in the visualisation. Default is "" (no message).
    ansi -- True if you want to use ANSI control codes to enrich the output.
        Compatible with terminals supporting ANSI control codes. Default
        False.
    compact -- True if you want to use a compact board visualisation,
        False to use a bigger one including axial coordinates along with
        the printable information in each hex. Default True (small board).
    
    Any other keyword arguments are passed through to the print function.

    Example:

        >>> board_dict = {
        ...     ( 0, 0): "hello",
        ...     ( 0, 2): "world",
        ...     ( 3,-2): "(p)",
        ...     ( 2,-1): "(S)",
        ...     (-4, 0): "(R)",
        ... }
        >>> print_board(board_dict, "message goes here", ansi=False)
        # message goes here
        #              .-'-._.-'-._.-'-._.-'-._.-'-.
        #             |     |     |     |     |     |
        #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #          |     |     | (p) |     |     |     |
        #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #       |     |     |     | (S) |     |     |     |
        #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #    |     |     |     |     |     |     |     |     |
        #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        # |     |     |     |     |hello|     |world|     |     |
        # '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #    |     |     |     |     |     |     |     |     |
        #    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #       |     |     |     |     |     |     |     |
        #       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #          |     |     |     |     |     |     |
        #          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #             | (R) |     |     |     |     |
        #             '-._.-'-._.-'-._.-'-._.-'-._.-'
    """
    if compact:
        template = """# {00:}
#              .-'-._.-'-._.-'-._.-'-._.-'-.
#             |{57:}|{58:}|{59:}|{60:}|{61:}|
#           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#          |{51:}|{52:}|{53:}|{54:}|{55:}|{56:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#       |{44:}|{45:}|{46:}|{47:}|{48:}|{49:}|{50:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{36:}|{37:}|{38:}|{39:}|{40:}|{41:}|{42:}|{43:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{27:}|{28:}|{29:}|{30:}|{31:}|{32:}|{33:}|{34:}|{35:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{19:}|{20:}|{21:}|{22:}|{23:}|{24:}|{25:}|{26:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{12:}|{13:}|{14:}|{15:}|{16:}|{17:}|{18:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{06:}|{07:}|{08:}|{09:}|{10:}|{11:}|
#          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#             |{01:}|{02:}|{03:}|{04:}|{05:}|
#             '-._.-'-._.-'-._.-'-._.-'-._.-'"""
    else:
        template = """# {00:}
#                  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#                 | {57:} | {58:} | {59:} | {60:} | {61:} |
#                 |  4,-4 |  4,-3 |  4,-2 |  4,-1 |  4, 0 |
#              ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#             | {51:} | {52:} | {53:} | {54:} | {55:} | {56:} |
#             |  3,-4 |  3,-3 |  3,-2 |  3,-1 |  3, 0 |  3, 1 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {44:} | {45:} | {46:} | {47:} | {48:} | {49:} | {50:} |
#         |  2,-4 |  2,-3 |  2,-2 |  2,-1 |  2, 0 |  2, 1 |  2, 2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {36:} | {37:} | {38:} | {39:} | {40:} | {41:} | {42:} | {43:} |
#     |  1,-4 |  1,-3 |  1,-2 |  1,-1 |  1, 0 |  1, 1 |  1, 2 |  1, 3 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {27:} | {28:} | {29:} | {30:} | {31:} | {32:} | {33:} | {34:} | {35:} |
# |  0,-4 |  0,-3 |  0,-2 |  0,-1 |  0, 0 |  0, 1 |  0, 2 |  0, 3 |  0, 4 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {19:} | {20:} | {21:} | {22:} | {23:} | {24:} | {25:} | {26:} |
#     | -1,-3 | -1,-2 | -1,-1 | -1, 0 | -1, 1 | -1, 2 | -1, 3 | -1, 4 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {12:} | {13:} | {14:} | {15:} | {16:} | {17:} | {18:} |
#         | -2,-2 | -2,-1 | -2, 0 | -2, 1 | -2, 2 | -2, 3 | -2, 4 |
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#             | {06:} | {07:} | {08:} | {09:} | {10:} | {11:} |
#             | -3,-1 | -3, 0 | -3, 1 | -3, 2 | -3, 3 | -3, 4 |   key:
#              `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'     ,-' `-.
#                 | {01:} | {02:} | {03:} | {04:} | {05:} |       | input |
#                 | -4, 0 | -4, 1 | -4, 2 | -4, 3 | -4, 4 |       |  r, q |
#                  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'         `-._,-'"""
    # prepare the provided board contents as strings, formatted to size.
    ran = range(-4, +4+1)
    cells = []
    for rq in [(r,q) for r in ran for q in ran if -r-q in ran]:
        if rq in board_dict:
            cell = str(board_dict[rq]).center(5)
            if ansi:
                # put contents in bold
                cell = f"\033[1m{cell}\033[0m"
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)
    # prepare the message, formatted across multiple lines
    multiline_message = "\n# ".join(message.splitlines())
    # fill in the template to create the board drawing, then print!
    board = template.format(multiline_message, *cells)
    print(board, **kwargs)
