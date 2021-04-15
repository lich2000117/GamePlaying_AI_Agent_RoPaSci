"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
# from search.util import print_board, print_slide, print_swing, load_json_data
from search.util import *
from search.search_algorithms import *
import copy

def main():

    ## board dict is used to show each turn
    board_dict = {}

    # play_dict is used to store symbols for each player
    play_dict = {"upper":{"R":[], "P":[], "S":[]},
                    "lower":{"R":[], "P":[], "S":[]},
                    "block":[]}                     
                    # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)

    # target_dict is used to store relationship between 2 symbols
    target_dict = {"R":"S", "S":"P", "P":"R"}

    # next board dict is used to store symbols of next turn
    next_board_dict = copy.deepcopy(play_dict) 

    ## Open Json File and read in input
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
            #load json file data into board_dict
            load_json_data(board_dict,data)
            board_cognition(board_dict, play_dict)

    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    #print initial board 
    # print_board(board_dict, message="", compact=True, ansi=False)
    
    # using Search Algorithm
    # print(play_dict, "\n")
    # print(next_board_dict, "\n")
    # print(board_dict, "\n")

    # after reading in initial state, start game in turn1
    turn = 1
    
    # initilize unmoveable symbols(lower's tokens and blocks) in next_board_dict
    initialize_board_for_next_turn(next_board_dict, board_dict)
    # print("__________________After initialization______________________\n")
    # print(play_dict, "\n")
    # print(next_board_dict, "\n")
    # print(board_dict, "\n")

    while not isGameEnded(board_dict):

        # move phase
        # upper moves all its tokens by one step in one turn 
        # print("*******************Turn: ", turn, "********************\n")

        ## tatics: let upper symbols, which has target symbol, move first to avoid jam created by upper symbols
        first_move_list = []
        last_move_list = []
        for upper_symbol in target_dict.keys():
            if (find_player_symbols(play_dict, "upper", upper_symbol)):
                if play_dict["lower"][target_dict[upper_symbol]]:
                    first_move_list.append(upper_symbol)
                else:
                    last_move_list.append(upper_symbol)
        move_list = first_move_list + last_move_list
        
        for single_symbol in move_list:
            # start from "Rock" symbols, then "Sissors", and "Paper"
            if (find_player_symbols(play_dict, "upper", single_symbol)):
                # a list of coordinators of upper player's symbols 
                token_list = play_dict["upper"][single_symbol] 
                i = 0
                # move every "Rock", "Sissors" & "Paper" sequentially
                while i < len(token_list):
                    start = token_list[i]
                    target_list = play_dict["lower"][target_dict[single_symbol]]
                    if not target_list:
                        # symbol which does not have a target makes a random move
                        random_move(single_symbol, start, play_dict, next_board_dict, turn)
                    else:
                        target = target_list[0] 
                        # BFS search, dodges blocks, returns a path
                        path = Search_Path(single_symbol, start, target, play_dict, next_board_dict) 
                        # only take second step in the BFS solution
                        next_step = path[1]
                        # print("path: ", path)
                        # print("next step: ", next_step)
                        move_token(single_symbol, start, next_step, next_board_dict, turn)
                    i += 1

        # update phase      
        # update board to deal with possible elimination 
        board_dict = {}
        update_board_dict(board_dict, next_board_dict, target_dict)
        # print_board(board_dict, message="", compact=True, ansi=False)

        # next turn
        turn += 1
        # copy next_board_dict to play_dict to be used in next turn
        play_dict = copy.deepcopy(next_board_dict)
        for key in next_board_dict["upper"].keys():
            next_board_dict["upper"][key] = []


    # print("the game has ended!\n")








    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
