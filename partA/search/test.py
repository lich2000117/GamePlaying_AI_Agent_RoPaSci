import sys
import json
import os

# Test util functions
from util import *

play_dict = {"upper":{"R":[], "P":[], "S":[]},
                    "lower":{"R":[], "P":[], "S":[]},
                    "block":[]}                     # "R":[(1,3),(3,4)]   saying Rock at position (1,3) and (3,4)

target = (1,2)

board_dict = {(0,1): "block",(1,1):"block"}

str_in = "0,0"


tup = tuple(map(int, str_in.split(",")))


Search_Path(tup, target, play_dict)

# #print(get_children(play_dict, tup))
# board_dict[tup] = "C_N"  #center node
# for p in get_children(play_dict, tup):
#     board_dict[p] = "Node"
# print_board(board_dict, message="", compact=True, ansi=False)


# board_dict[target] = "targt"

# if (tup == target):
#     print("##### GOT the TARGET #######")